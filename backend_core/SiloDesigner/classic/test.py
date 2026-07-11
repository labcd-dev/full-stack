# import numpy as np
# from backend_core.Tuner.src.systems import DCMotorPositionControl
# from backend_core.tests.test_utils import compareMatlab
#
# np.random.seed(42)
#
# control_params_dc_fsf = {
#     "K1": 5.728,
#     "K2": 44.27,
#     "K3": 100
# }
#
# scenario_dc_1 = {
#     "id": "I",
#     "initial_condition_range": [np.pi, np.pi],
#     "randomness_level": 0,
#     "disturbance_level": 0,
#     "param_uncertainty": 0,
# }
#
# compareMatlab(DCMotorPositionControl, control_params_dc_fsf, scenario_dc_1)