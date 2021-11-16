import numpy as np

def random_light(self):
    # Random light
    sh_coeffs = 0.7 * (2 * np.random.rand(9) - 1)
    # Ambient light (first coeff) needs a minimum  is ambient. Rest is uniformly distributed, higher means brighter.
    sh_coeffs[0] = 0.5 + 0.9 * np.random.rand()
    sh_coeffs[1] = -0.7 * np.random.rand()
    return sh_coeffs