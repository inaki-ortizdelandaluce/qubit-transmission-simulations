import numpy as np
import cmath
import math

X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1.j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])


class Qubit:
    def __init__(self, ket=np.array([1, 0])):
        """
        Initializes a qubit in the computational basis. If no arguments are provided, it returns the zero state.

        Parameters
        ---------
        ket : ndarray
            The qubit components in the computational basis in a 1-d complex array.
        """
        self.alpha = complex(ket[0])
        self.beta = complex(ket[1])
        self.normalize()

    def __repr__(self):
        return '{} |0> + {} |1>'.format(self.alpha, self.beta)

    def ket(self):
        return np.array([self.alpha, self.beta], dtype=np.complex_)

    def normalize(self):
        arr = self.ket()
        self.alpha, self.beta = arr/np.linalg.norm(arr)

    def rho(self):
        """
         Return the density matrix corresponding to the qubit in a pure state.

         Returns
         -------
         ndarray
             A 2x2 density matrix corresponding to the qubit in a pure state.
         """
        return np.outer(self.ket(), self.ket().conj())

    def bloch_angles(self):
        """
        Return the spherical coordinates of the qubit in the Bloch sphere, with polar and azimuthal angles in radians.

        Returns
        -------
        (float, float)
            The Bloch sphere coordinates, first the polar angle and then the azimuthal angle (both in radians).
        """
        r0, phi0 = cmath.polar(self.alpha)
        r1, phi1 = cmath.polar(self.beta)
        theta = 2 * math.acos(r0)
        phi = phi1 - phi0

        return theta, phi

    @staticmethod
    def density2bloch(rho):
        """
         Return the cartesian coordinates of the specified qubit state in the Bloch sphere.

        Parameters
        ---------
        rho : ndarray
            The qubit state in density matrix form

         Returns
         -------
         (float, float, float)
             The cartesian coordinates of the qubit in the Bloch sphere (xyz).

        """
        # cast complex to real to avoid throwing ComplexWarning, imaginary part should always be zero
        return [np.real(np.trace(np.matmul(rho, sigma))) for sigma in np.array([X, Y, Z])]

    def bloch_vector(self):
        """
         Return the cartesian coordinates of the qubit in the Bloch sphere.

         Returns
         -------
         (float, float, float)
             The cartesian coordinates of the qubit in the Bloch sphere (xyz).

         """
        return Qubit.density2bloch(self.rho())
