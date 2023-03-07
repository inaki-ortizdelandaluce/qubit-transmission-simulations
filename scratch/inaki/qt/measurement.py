import numpy as np
import scipy
from qt.qubit import Qubit


class PVM:
    def __init__(self, qubit: Qubit):
        """
        Creates a PVM with the elements corresponding to the specified qubit state.

        Parameters
        ---------
        qubit : Qubit
            The specified qubit state from which the two pb1[0]rank-1 projectors are generated.
        """
        rho = qubit.rho()
        sigma = np.identity(2) - rho
        self.bloch = np.array([Qubit.density2bloch(rho), Qubit.density2bloch(sigma)])
        self.proj = np.array([rho, sigma])

    def projector(self, index):
        """
        Returns rank-1 projector for the corresponding index

        Parameters
        ---------
        index : the projector index

        Returns
        -------
        ndarray
                A 2-d array with the corresponding projector.
        """
        return self.proj[index]

    def probability(self, qubit: Qubit):
        """
        Returns the probabilities of the different outcomes for a given qubit state

        Parameters
        ---------
        qubit : the qubit state

        Returns
        -------
        ndarray
                The probabilities for each outcome given the input state, stored in a 1-d array.
        """

        # repeat density matrix along zero axis
        rho = qubit.rho()
        rho = np.repeat(rho[np.newaxis, :, :], self.proj.shape[0], axis=0)

        # compute trace of projectors by density matrix
        return np.real(np.trace(np.matmul(self.proj, rho), axis1=1, axis2=2))


class POVM:

    def __init__(self, weights, proj):
        """
         Creates a POVM with the specified weights and rank-1 projectors.

         Parameters
         ---------
         weights : ndarray
            The positive coefficients of the constituting rank-1 projectors.

         proj : ndarray
            A 3-d array with the constituting rank-1 projectors.

        """
        self.weights = weights
        self.elements = proj * weights[:, np.newaxis, np.newaxis]
        self.bloch = v = np.asarray([Qubit.density2bloch(p) for p in proj])

    @classmethod
    def new(cls, qubits):
        """
         Creates a POVM with the rank-1 projectors corresponding to the specified qubit states.

         Parameters
         ---------
         qubits : ndarray
            The specified array of N-2 qubit states from which the N rank-1 POVM projectors are generated.
        """
        # last element normalizes all POVM elements
        rhos = np.asarray([q.rho() for q in qubits])
        e = np.identity(2) - np.sum(rhos, axis=0)

        # diagonalize last element to obtain remaining rank-1 projectors
        _, w = np.linalg.eig(e)
        q1 = Qubit(w[:, 0])
        q2 = Qubit(w[:, 1])
        qubits = np.append(qubits, np.array([q1, q2]), axis=0)

        # compute POVM weights and elements as a linear program (see Sentís et al. 2013)
        v = np.asarray([q.bloch_vector() for q in qubits])
        n = len(qubits)

        a = np.vstack((np.ones((n,)), v.T))
        b = np.append(np.array([2]), np.zeros(n - 1, ), axis=0)

        lp = scipy.optimize.linprog(np.ones(n, ), A_eq=a, b_eq=b, bounds=(0.01, 1), method='highs')
        _a, _e = lp['x'], np.asarray([q.rho() for q in qubits])

        return cls(_a, _e)

    def element(self, index):
        """
        Returns the POVM element for the corresponding index

        Parameters
        ---------
        index : the POVM element index

        Returns
        -------
        ndarray
                A 2-d array with the corresponding POVM element.
        """
        return self.element[index]

    def probability(self, qubit: Qubit):
        """
        Returns the probabilities of the different outcomes for a given qubit state

        Parameters
        ---------
        qubit : the qubit state

        Returns
        -------
        ndarray
                The probabilities for each outcome given the input state, stored in a 1-d array.
        """

        # repeat density matrix along zero axis
        rho = qubit.rho()
        rho = np.repeat(rho[np.newaxis, :, :], self.elements.shape[0], axis=0)

        # compute trace of projectors by density matrix
        return np.real(np.trace(np.matmul(self.elements, rho), axis1=1, axis2=2))
