"""
input_handlers.py - File input and predefined system handling

This module provides handlers for:
- File selection via GUI dialog or manual input
- Predefined system selection
- Input parsing utilities
"""

import os
import platform
if platform.system() == "Windows":
    import tkinter as tk
    from tkinter import filedialog
from typing import Dict, Any, Optional, Union


class InputHandlers:
    """
    Handles various input methods for system configuration:
    - File selection (GUI or manual)
    - Predefined system selection
    - Key-value input parsing
    """
    
    # Predefined system configurations
    PREDEFINED_SYSTEMS = {
        '1': {
            'name': 'Mass-Spring-Damper',
            'description': 'Classic mechanical oscillator',
            'config': {
                'system_name': 'Mass_Spring_Damper',
                'params': {'m': 2.0, 'c': 0.5, 'k': 10.0, 'desired_force': 5.0},
                'operating_conditions': {'desired_force': 5.0},
                'bounds': {
                    'x_min': [-10.0, -10.0],
                    'x_max': [10.0, 10.0],
                    'u_min': [0.0],
                    'u_max': [20.0]
                },
                'n_x': 2,
                'n_u': 1,
                'state_vars': ['position [m]', 'velocity [m/s]'],
                'input_vars': ['force [N]'],
                'param_vars': ['m', 'c', 'k', 'desired_force'],
                'system_f_code': '''
import numpy as np
def system_f(x, u, params):
    m = params['m']
    c = params['c']
    k = params['k']
    position = x[0]
    velocity = x[1]
    force = u[0]
    # Dynamics: dx/dt = v, dv/dt = (F - c*v - k*x)/m
    dxdt = velocity
    dvdt = (force - c * velocity - k * position) / m
    return np.array([dxdt, dvdt])
'''
            }
        },
        '2': {
            'name': 'Inverted Pendulum',
            'description': 'Classic control problem',
            'config': {
                'system_name': 'Inverted_Pendulum',
                'params': {'m': 0.5, 'M': 2.0, 'L': 0.5, 'g': 9.81, 'b': 0.1},
                'operating_conditions': {'theta': 0.0, 'x_cart': 0.0},
                'bounds': {
                    'x_min': [-5.0, -10.0, -3.14, -10.0],
                    'x_max': [5.0, 10.0, 3.14, 10.0],
                    'u_min': [-50.0],
                    'u_max': [50.0]
                },
                'n_x': 4,
                'n_u': 1,
                'state_vars': ['x_cart [m]', 'x_dot [m/s]', 'theta [rad]', 'theta_dot [rad/s]'],
                'input_vars': ['force [N]'],
                'param_vars': ['m', 'M', 'L', 'g', 'b'],
                'system_f_code': '''
import numpy as np
def system_f(x, u, params):
    m, M, L, g, b = params['m'], params['M'], params['L'], params['g'], params['b']
    x_cart, x_dot, theta, theta_dot = x
    F = u[0]
    # Simplified inverted pendulum dynamics
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    denom = M + m * sin_theta**2
    x_ddot = (F - b * x_dot + m * L * theta_dot**2 * sin_theta - m * g * sin_theta * cos_theta) / denom
    theta_ddot = (-F * cos_theta + b * x_dot * cos_theta - m * L * theta_dot**2 * sin_theta * cos_theta + (M + m) * g * sin_theta) / (L * denom)
    return np.array([x_dot, x_ddot, theta_dot, theta_ddot])
'''
            }
        },
        '3': {
            'name': 'Aircraft Longitudinal',
            'description': 'Simplified aircraft longitudinal dynamics',
            'config': {
                'system_name': 'Aircraft_Longitudinal',
                'params': {
                    'm': 1000.0, 'g': 9.81, 'rho': 1.225, 'S': 16.0,
                    'c': 1.5, 'I_yy': 1000.0, 'T_max': 5000.0,
                    'C_L0': 0.2, 'C_Lalpha': 5.0, 'C_Lq': 0.0, 'C_Ldelta': 0.5,
                    'C_D0': 0.02, 'k': 0.05,
                    'C_m0': 0.0, 'C_malpha': -1.0, 'C_mq': -10.0, 'C_mdelta': -1.5
                },
                'operating_conditions': {'airspeed': 50.0},
                'bounds': {
                    'x_min': [20.0, -0.2, -1.0, -0.2],
                    'x_max': [100.0, 0.5, 1.0, 0.5],
                    'u_min': [-0.5],
                    'u_max': [0.5]
                },
                'n_x': 4,
                'n_u': 1,
                'state_vars': ['V [m/s]', 'α [rad]', 'q [rad/s]', 'θ [rad]'],
                'input_vars': ['δ_e [rad]'],
                'param_vars': ['m', 'g', 'rho', 'S', 'c', 'I_yy', 'T_max', 
                               'C_L0', 'C_Lalpha', 'C_Lq', 'C_Ldelta',
                               'C_D0', 'k', 'C_m0', 'C_malpha', 'C_mq', 'C_mdelta'],
                'system_f_code': '''
import numpy as np
def system_f(x, u, params):
    V, alpha, q, theta = x
    delta_e = u[0]
    m = params['m']
    g = params['g']
    rho = params['rho']
    S = params['S']
    c = params['c']
    I_yy = params['I_yy']
    T_max = params['T_max']
    C_L0 = params['C_L0']
    C_Lalpha = params['C_Lalpha']
    C_Lq = params['C_Lq']
    C_Ldelta = params['C_Ldelta']
    C_D0 = params['C_D0']
    k = params['k']
    C_m0 = params['C_m0']
    C_malpha = params['C_malpha']
    C_mq = params['C_mq']
    C_mdelta = params['C_mdelta']
    
    # Aerodynamic coefficients
    C_L = C_L0 + C_Lalpha * alpha + C_Lq * (c / (2 * V)) * q + C_Ldelta * delta_e
    C_D = C_D0 + k * C_L**2
    C_m = C_m0 + C_malpha * alpha + C_mq * (c / (2 * V)) * q + C_mdelta * delta_e
    
    # Forces and moments
    L = 0.5 * rho * V**2 * S * C_L
    D = 0.5 * rho * V**2 * S * C_D
    M = 0.5 * rho * V**2 * S * c * C_m
    
    # Thrust (simplified: constant for now, could be another input)
    T = 0.5 * T_max  # 50% throttle
    
    # Equations of motion
    gamma = theta - alpha  # flight path angle
    V_dot = (T * np.cos(alpha) - D - m * g * np.sin(gamma)) / m
    alpha_dot = (-T * np.sin(alpha) - L + m * g * np.cos(gamma)) / (m * V) + q
    q_dot = M / I_yy
    theta_dot = q
    
    return np.array([V_dot, alpha_dot, q_dot, theta_dot])
'''
            }
        }
    }

    @staticmethod
    def _parse_key_value_input(user_input: str) -> Dict[str, Any]:
        """
        Convert simple key-value input to dictionary.
        
        Examples:
        - "m: 1.0, c: 0.5, k: 10.0" → {"m": 1.0, "c": 0.5, "k": 10.0}
        - "mode: hover, desired: 5" → {"mode": "hover", "desired": 5}
        
        Args:
            user_input: String with key:value pairs separated by commas
            
        Returns:
            Dictionary of parsed key-value pairs
        """
        result = {}
        pairs = user_input.split(',')
        for pair in pairs:
            if ':' not in pair:
                continue
            key, value = pair.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Try to convert to number, otherwise keep as string
            try:
                if '.' in value:
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except ValueError:
                # Keep as string
                result[key] = value

        return result

    @staticmethod
    def _parse_bounds_input(user_input: str) -> Dict[str, Any]:
        """
        Parse bounds input string to dictionary.
        
        Example: "x_min: -10, -10; x_max: 10, 10; u_min: 0; u_max: 10"
        Returns: {"x_min": [-10, -10], "x_max": [10, 10], "u_min": [0], "u_max": [10]}
        
        Args:
            user_input: String with bounds definitions
            
        Returns:
            Dictionary with parsed bounds
        """
        result = {}
        fields = user_input.split(';')

        for field in fields:
            if ':' not in field:
                continue
            key, values_str = field.split(':', 1)
            key = key.strip()
            values_str = values_str.strip()

            # Parse comma-separated values as a list
            try:
                values = [float(v.strip()) for v in values_str.split(',') if v.strip()]
                result[key] = values
            except ValueError:
                print(f"    ⚠ Could not parse values for {key}: {values_str}")
                result[key] = []

        return result

    @staticmethod
    def get_file_path() -> Optional[str]:
        """
        Get file path using GUI dialog or manual input.
        
        Returns:
            File path string or None if cancelled
        """
        file_path = ""
        gui_failed = False

        print("\n📂 Opening file dialog... (select a .py, .m, or .txt file)")
        try:
            # Create Tk root window with better Windows compatibility
            root = tk.Tk()
            root.withdraw()
            # Force to front on Windows
            root.attributes('-topmost', True)
            root.after(100, lambda: root.attributes('-topmost', False))
            
            file_path = filedialog.askopenfilename(
                title="Select System Definition File",
                filetypes=[
                    ("Python files", "*.py"),
                    ("MATLAB files", "*.m"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            root.destroy()
            
            if not file_path:
                print("   No file selected.")
                return None
                
        except Exception as e:
            print(f"   ⚠ GUI dialog failed: {e}")
            gui_failed = True

        if gui_failed or not file_path:
            # Fallback to manual input
            print("\n   Please enter the file path manually:")
            file_path = input("   File path: ").strip()
            if not file_path:
                print("   No file path provided.")
                return None

        # Validate file exists
        if not os.path.isfile(file_path):
            print(f"   ⚠ File not found: {file_path}")
            return None

        print(f"   ✓ Selected file: {file_path}")
        return file_path

    @staticmethod
    def get_predefined_system() -> Union[str, Dict[str, Any]]:
        """
        Display predefined system options and get user selection.
        
        Returns:
            Either a string description (for LLM parsing) or a complete config dict
        """
        print("\n📋 Predefined Systems:")
        print("1. Mass-Spring-Damper (Classic mechanical oscillator)")
        print("2. Inverted Pendulum (Classic control problem)")
        print("3. Aircraft Longitudinal (Simplified flight dynamics)")
        print("4. Load from customized_system.py")
        
        sub_choice = input("\nSelect system (1-4): ").strip()
        
        if sub_choice in InputHandlers.PREDEFINED_SYSTEMS:
            system_info = InputHandlers.PREDEFINED_SYSTEMS[sub_choice]
            print(f"\n📖 {system_info['name']}: {system_info['description']}")
            print(f"\nDefault configuration:")
            config = system_info['config']
            print(f"  Parameters: {config['params']}")
            print(f"  Operating conditions: {config['operating_conditions']}")
            print(f"  State variables: {config['state_vars']}")
            print(f"  Input variables: {config['input_vars']}")
            
            use_default = input("\nUse default configuration? (y/n) [default=y]: ").strip().lower()
            if use_default != 'n':
                return config  # Return complete config directly
            
            # Otherwise, return description for LLM parsing with modifications
            return f"""
A {config['system_name'].replace('_', ' ').lower()} system with the following parameters:
{chr(10).join(f'  {k} = {v}' for k, v in config['params'].items())}

Operating Conditions:
{chr(10).join(f'  {k} = {v}' for k, v in config['operating_conditions'].items())}

State Bounds:
  x_min = {config['bounds']['x_min']}
  x_max = {config['bounds']['x_max']}

Input Bounds:
  u_min = {config['bounds']['u_min']}
  u_max = {config['bounds']['u_max']}

State variable names: {config['state_vars']}
Input variable names: {config['input_vars']}
Parameter names: {config['param_vars']}
"""
        
        elif sub_choice == '4':
            # Load from customized_system.py
            return InputHandlers._load_custom_system()
        
        else:
            print("Invalid choice. Defaulting to Mass-Spring-Damper.")
            return "A mass-spring-damper system with mass 2kg, damping 0.5 Ns/m, stiffness 10 N/m, desired force 5N"

    @staticmethod
    def _load_custom_system() -> Union[str, Dict[str, Any]]:
        """
        Attempt to load custom systems from customized_system.py module.
        
        Returns:
            Either a config dict or description string
        """
        try:
            import customized_system
            available_systems = customized_system.get_available_systems()
            if not available_systems:
                print("No custom systems available. Please describe your system.")
                return input("Describe your system: ").strip()
            else:
                print("\nAvailable Custom Systems:")
                for i, sys_name in enumerate(available_systems, 1):
                    print(f"{i}. {sys_name}")
                sub_sub_choice = input(f"Select custom system (1-{len(available_systems)}): ").strip()
                try:
                    idx = int(sub_sub_choice) - 1
                    if 0 <= idx < len(available_systems):
                        system_name = available_systems[idx]
                        config = customized_system.get_system_config(system_name)
                        config['system_name'] = system_name
                        return config  # Return config directly for custom systems
                    else:
                        print("Invalid choice. Please describe your system.")
                        return input("Describe your system: ").strip()
                except ValueError:
                    print("Invalid choice. Please describe your system.")
                    return input("Describe your system: ").strip()
        except ImportError:
            print("Customized systems not available. Please describe your system.")
            return input("Describe your system: ").strip()
