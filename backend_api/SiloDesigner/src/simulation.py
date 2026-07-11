import numpy as np
from backend_api.SiloDesigner.src.systems import GeneralDynamicalSystem
from typing import Optional


class SimulationRunner:
    def __init__(self, system_class: type[GeneralDynamicalSystem]):
        self.system_class = system_class
        self.system: Optional[GeneralDynamicalSystem] = None
        # Store configuration parameters
        self._config = {}

    def set_config(self, **kwargs):
        """Store configuration parameters to apply to all system instances"""
        self._config.update(kwargs)

    def set_scenario(self, scenario: dict) -> GeneralDynamicalSystem:
        self.system = self.system_class(scenario)
        # Apply stored configuration
        for key, value in self._config.items():
            if hasattr(self.system, key):
                setattr(self.system, key, value)
        return self.system

    def calculate_metrics(self, errors, control_signals):
        """Calculate performance metrics using the configured output channel"""
        metrics = {}
        t = np.arange(0, len(errors) * self.system.dt, self.system.dt)

        # errors is already the error for the output channel from simulations
        # So we use it directly
        output_errors = errors

        # Mean Squared Error
        metrics['mse'] = np.mean(output_errors ** 2)
        metrics['rmse'] = np.sqrt(np.mean(output_errors ** 2))

        # Get initial error
        initial_error = np.abs(output_errors[0])

        # Settling time - time when system enters and stays within 5% threshold
        threshold = 0.05 * initial_error if initial_error > 0 else 0.05

        # Find all indices where the system is within threshold
        settled_indices = np.where(np.abs(output_errors) < threshold)[0]

        if len(settled_indices) > 0:
            # Find consecutive settled indices
            consecutive_groups = []
            current_group = [settled_indices[0]]

            for i in range(1, len(settled_indices)):
                if settled_indices[i] == settled_indices[i - 1] + 1:
                    current_group.append(settled_indices[i])
                else:
                    if len(current_group) > 0:
                        consecutive_groups.append(current_group)
                    current_group = [settled_indices[i]]

            if len(current_group) > 0:
                consecutive_groups.append(current_group)

            # Find the longest consecutive sequence that continues to the end
            for group in consecutive_groups:
                if group[-1] == len(output_errors) - 1:
                    metrics['settling_time'] = t[group[0]]
                    break
            else:
                metrics['settling_time'] = np.inf
        else:
            metrics['settling_time'] = np.inf

        # Calculate percentage overshoot
        initial_error = np.abs(errors[0])  # Magnitude of initial error (== |initial_output| since target=0)
        if initial_error > 0:
            # Derive output trajectory: output = -errors (since errors = target - output = -output for target=0)
            outputs = -errors
            min_output = np.min(outputs)
            if min_output < 0:
                # Undershoot magnitude relative to initial step size (initial_output assumed positive)
                overshoot_amount = -min_output / initial_error
                metrics['overshoot'] = overshoot_amount * 100
            else:
                metrics['overshoot'] = 0.0
        else:
            metrics['overshoot'] = 0.0

        # Stability - check if simulation completed without diverging
        metrics['stable'] = len(output_errors) == int(self.system.max_time / self.system.dt)

        # Rise time - time to reach within 5% of target
        rise_threshold = 0.05 * initial_error if initial_error > 0 else 0.05
        rise_indices = np.where(np.abs(output_errors) < rise_threshold)[0]
        metrics['rise_time'] = t[rise_indices[0]] if rise_indices.size > 0 else np.inf

        # Zero-crossings (oscillations around target)
        zero_crossings = np.where(np.diff(np.signbit(output_errors)))[0]
        metrics['zero_crossings'] = len(zero_crossings)

        # Control effort
        metrics['control_effort'] = np.sum(np.abs(control_signals))

        # Control signal zero-crossings
        control_zero_crossings = np.where(np.diff(np.signbit(control_signals)))[0]
        metrics['control_zero_crossings'] = len(control_zero_crossings)

        # Steady-state error
        metrics['ss_error'] = np.abs(np.mean(output_errors[-int(0.1 * len(output_errors)):]))  # Last 10% of simulation

        return metrics

    def evaluate_parameters(self, params, initial_state=None):
        """Evaluate controller parameters on the system

        Args:
            params: Controller parameters dict
            initial_state: Optional fixed initial state for reproducible simulations
        """
        try:
            # Check controller type and call appropriate simulation
            if isinstance(params, dict):
                fsf_keys = [f"K{i + 1}" for i in range(self.system.num_states)]
                if any(key in params for key in fsf_keys):
                    # FSF controller
                    K_values = [params.get(f"K{i + 1}", 0.0)
                                for i in range(self.system.num_states)]
                    trajectory, control_signals, errors = self.system.run_fsf_simulation(
                        K_values, initial_state=initial_state, seed=self._config["seed"]
                    )
                else:
                    # PID controller
                    Kp = params.get('Kp', 0.0)
                    Ki = params.get('Ki', 0.0)
                    Kd = params.get('Kd', 0.0)
                    trajectory, control_signals, errors = self.system.run_pid_simulation(
                        Kp, Ki, Kd, initial_state=initial_state, seed=self._config["seed"]
                    )

            metrics = self.calculate_metrics(errors, control_signals)
            return {
                'success': True,
                'metrics': metrics,
                'trajectory': trajectory,
                'control_signals': control_signals,
                'errors': errors,
                'initial_state': initial_state if initial_state is not None else None  # Store IC used
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run_monte_carlo(self, params, num_runs=100):
        """Run Monte Carlo simulations and return aggregated metrics"""
        metrics_list = []
        for _ in range(num_runs):
            result = self.evaluate_parameters(params)
            if result['success']:
                metrics_list.append(result['metrics'])

        # Calculate statistics
        stats = {}
        if metrics_list:
            for key in metrics_list[0].keys():
                values = [m[key] for m in metrics_list]
                stats[key] = {
                    'mean': np.nanmean(values),
                    'std': np.nanstd(values)
                }
        return stats
