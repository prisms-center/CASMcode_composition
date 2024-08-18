import libcasm.composition as casmcomp
import numpy as np


class FormationEnergyCalculator:
    def __init__(
        self,
        end_state_compositions: np.ndarray,
        end_state_energies: np.ndarray,
    ):
        """Initialize formation energy calculator.

        For an :math:`m` dimensional parametric composition space,
        :math:`n = m+1` reference end states are required.


        Parameters
        ----------
        end_state_compositions: np.ndarray[m, n]
            The compositions of the :math:`n` end states with respect
            to the :math:`m` parametric composition axes as column
            vectors.
        end_state_energies: np.ndarray[n]
            The DFT energy of the end states normalized per
            primitive cell.
        """
        # find H matrix for barycentric coordinates
        ndim = end_state_compositions.shape[0]
        if not end_state_compositions.shape[1] == (ndim + 1):
            raise ValueError(
                f"for a space with {ndim} axes, provide {ndim+1} end states"
            )
        H = np.vstack((end_state_compositions, np.ones((1, ndim + 1))))
        H_inv = np.linalg.inv(H)
        self.H_inv = H_inv

        # save end state energies
        if not end_state_energies.shape[0] == (ndim + 1):
            raise ValueError(
                f"found {ndim+1} end states but {end_state_energies.shape[0]} energies"
            )
        self.end_state_energies = end_state_energies

    def get_formation_energy(self, points: np.ndarray, energies: np.ndarray):
        """Get the formation energy given parametric composition and energy.

        Parameters
        ----------
        points: np.ndarray[m, n]
            :math:`n` points in parametric composition space of dimension :math:`m`
        energies: np.ndarray[n]
            DFT energy for each point, normalized per primitive cell.

        Returns
        -------
        formation_energies: np.ndarray[n]
            Formation energy for each point, normalized per primitive cell.
        """
        # Find barycentric coordinates
        points = np.vstack((points, np.ones(points.shape[1])))
        barycentric_coordinates = self.H_inv @ points

        # Find reference energies
        reference_energies = self.end_state_energies @ barycentric_coordinates

        # Find distance from DFT energies to reference energies
        formation_energies = energies - reference_energies
        return formation_energies
