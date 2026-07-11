import numpy as np
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from backend_api.SiloDesigner.src.simulation import GeneralDynamicalSystem, SimulationRunner

np.random.seed(42)

def compareMatlab(system_class: type[GeneralDynamicalSystem], control_params, scenario_data, num_runs=100):
    all_theta = []
    all_control = []
    all_metrics = []

    # Run the simulation for each experiment
    for _ in range(num_runs):
        system = system_class(scenario_data)
        trajectory, control_signals, errors = system.run_simulation(control_params)
        sim = SimulationRunner(system_class)
        sim.set_scenario(scenario_data)
        metrics = sim.calculate_metrics(errors, control_signals)
        all_theta.append(trajectory)
        all_control.append(control_signals)
        all_metrics.append(metrics)

    # Process trajectories: find max length to standardize matrix size
    max_len = max(len(traj) for traj in all_theta)

    # Initialize matrices with NaN to handle varying lengths of trajectories
    # New shape: (num_runs, max_len, 7) for 7 variables in the trajectory
    theta_matrix = np.full((num_runs, max_len), np.nan)
    control_matrix = np.full((num_runs, max_len), np.nan)

    # Fill in the matrices with actual trajectory and control signal data
    for i in range(num_runs):
        theta_matrix[i, :len(all_theta[i])] = all_theta[i]
        control_matrix[i, :len(all_control[i])] = all_control[i]

    # Time response plot (same as before)
    theta_mean = np.degrees(np.nanmean(theta_matrix, axis=0))  # Now shape (max_len, 7)
    theta_std = np.degrees(np.nanstd(theta_matrix, axis=0))
    control_mean = np.nanmean(control_matrix, axis=0)
    control_std = np.nanstd(control_matrix, axis=0)
    time_vector = np.arange(0, max_len * 0.01, 0.01)[:max_len]

    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    ax1.plot(time_vector, theta_mean, 'b-', lw=2, label='Mean Angle (State 1)')
    ax1.fill_between(time_vector, theta_mean - theta_std, theta_mean + theta_std,
                     color='blue', alpha=0.2, label='Â±1 SD')
    # ax1.axhline(np.degrees(np.pi), color='r', linestyle='--', label='Target')
    ax1.set_ylabel('Angle (deg)')
    ax1.set_title(f'Average System Response ({num_runs} Runs)')
    ax1.legend(loc='upper right')
    ax1.grid(True)

    ax2.plot(time_vector, control_mean, 'g-', lw=2, label='Mean Control')
    ax2.fill_between(time_vector, control_mean - control_std, control_mean + control_std,
                     color='green', alpha=0.2, label='Â±1 SD')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Torque (Nm)')
    ax2.legend(loc='upper right')
    ax2.grid(True)
    plt.tight_layout()


    # Process metrics for each run
    metric_groups = [
        ['mse'],
        ['control_effort', 'overshoot'],
        ['settling_time', 'rise_time'],
        ['zero_crossings', 'control_zero_crossings']
    ]

    metric_labels = {
        'mse': 'MSE',
        'settling_time': 'Settling Time (s)',
        'rise_time': 'Rise Time (s)',
        'overshoot': 'Overshoot (%)',
        'zero_crossings': 'Zero Crossings',
        'control_zero_crossings': 'Control ZC',
        'control_effort': 'Control Effort'
    }

    # Collect all metrics
    metrics_dict = {k: [] for k in all_metrics[0].keys()}
    for m in all_metrics:
        for k in metrics_dict.keys():
            metrics_dict[k].append(m[k])

    # Handle infinite values for settling time and rise time
    metrics_dict['settling_time'] = np.where(
        np.isinf(metrics_dict['settling_time']),
        np.nan,
        metrics_dict['settling_time']
    )
    metrics_dict['rise_time'] = np.where(
        np.isinf(metrics_dict['rise_time']),
        np.nan,
        metrics_dict['rise_time']
    )

    # Calculate statistics (mean, std) for metrics
    stats = {
        'means': {k: np.nanmean(metrics_dict[k]) for k in metrics_dict},
        'stds': {k: np.nanstd(metrics_dict[k]) for k in metrics_dict},
        'stability_rate': np.mean(metrics_dict['stable'])
    }

    # Create grouped metric plots
    fig2, axs = plt.subplots(2, 2, figsize=(8, 4))
    axs = axs.ravel()

    for i, group in enumerate(metric_groups):
        ax = axs[i]
        x = np.arange(len(group))
        means = [stats['means'][k] for k in group]
        stds = [stats['stds'][k] for k in group]

        bars = ax.bar(x, means, yerr=stds, align='center', alpha=0.7,
                      color=f'C{i}', capsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels([metric_labels[k] for k in group])
        ax.set_title(f"{' vs. '.join([metric_labels[k] for k in group])}")
        ax.grid(True, axis='y', linestyle='--')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')

    # Add stability rate as text in the last subplot
    axs[-1].text(0.5, 0.9, f"Stability Rate: {stats['stability_rate']:.1%}",
                 ha='center', va='center', transform=axs[-1].transAxes,
                 bbox=dict(facecolor='white', edgecolor='gray'))

    plt.suptitle(f'Performance Metrics ({num_runs} Runs)', y=1.02)
    plt.tight_layout()
    plt.show()

    # Print summary of statistics
    print(f"\n{' Metric ':â”^15} {' Mean ':^10} {' Std ':^15}")
    print(f"{'MSE':<15} | {stats['means']['mse']:>8.4f}      | {stats['stds']['mse']:>8.4f}")
    print(
        f"{'Settling Time':<15} | {stats['means']['settling_time']:>8.2f}      | {stats['stds']['settling_time']:>8.2f}")
    print(f"{'Rise Time':<15} | {stats['means']['rise_time']:>8.2f}      | {stats['stds']['rise_time']:>8.2f}")
    print(f"{'Overshoot (%)':<15} | {stats['means']['overshoot']:>8.2f}      | {stats['stds']['overshoot']:>8.2f}")
    print(
        f"{'Zero Crossings':<15} | {stats['means']['zero_crossings']:>8.2f}      | {stats['stds']['zero_crossings']:>8.2f}")
    print(
        f"{'Control ZC':<15} | {stats['means']['control_zero_crossings']:>8.2f}      | {stats['stds']['control_zero_crossings']:>8.2f}")
    print(
        f"{'Control Effort':<15} | {stats['means']['control_effort']:>8.2f}      | {stats['stds']['control_effort']:>8.2f}")
    print(f"{'Stability Rate':<15} | {stats['stability_rate']:>8.2%}      | {'â€”':^8}")
