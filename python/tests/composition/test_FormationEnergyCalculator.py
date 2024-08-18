import json
import numpy as np
import libcasm.xtal as xtal
from libcasm.composition import CompositionConverter, FormationEnergyCalculator


def test_binary():
    # read data
    with open("li_ag_bcc_relax_vasp_data.json", "r") as f:
        data = json.load(f)
    true_formation_energies = np.array(
        [i["formation_energy_per_atom"] for i in data.values()]
    )
    energies = np.array([i["energy_per_atom"] for i in data.values()])
    comp = np.array([i["comp"] for i in data.values()]).reshape(1, -1)
    ref_Ag_energy = -2.717411600000
    ref_Li_energy = -1.904210800000

    # calculate formation energies
    end_state_compositions = np.array([[0, 1]])  # Li=0, Li=1
    end_state_energies = np.array([ref_Ag_energy, ref_Li_energy])
    formation_energy_calculator = FormationEnergyCalculator(
        end_state_compositions, end_state_energies
    )
    formation_energies = formation_energy_calculator.get_formation_energy(
        points=comp, energies=energies
    )
    assert np.all(
        np.isclose(formation_energies - true_formation_energies, 0, atol=1e-6)
    )


def test_quaternary():
    # read data
    with open("jonathan_data/test_tino_comp_data.json", "r") as f:
        data = json.load(f)
    true_formation_energies = np.array([i["formation_energy"] for i in data])
    energies = np.array([i["energy"] for i in data])
    comp = np.hstack([i["comp"] for i in data])

    # get references per primitive cell
    ## reference parametric compositions
    components = ["N", "O", "Va", "Ti"]
    origin_and_end_members = [
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [1, 0, 0, 2],
        [1, 1, 1, 0],
    ]
    composition_converter = CompositionConverter(
        components=components, origin_and_end_members=origin_and_end_members
    )
    ref_Ti_comp = composition_converter.param_composition([0, 0, 0, 2])
    ref_Ti4NO3_comp = composition_converter.param_composition([0.25, 0.75, 0, 1])
    ref_Ti2N2O_comp = composition_converter.param_composition([0.8, 0.4, 0, 0.8])
    ref_Va_comp = composition_converter.param_composition([0, 0, 2, 0])
    ## reference energies
    ref_Ti_energy = -15.974669000000 * 2
    ref_Ti4NO3_energy = -13.969243750000 * 2
    ref_Ti2N2O_energy = -13.432652200000 * 2
    ref_Va_energy = 0

    # calculate formation energies
    end_state_compositions = np.array(
        [ref_Ti_comp, ref_Ti4NO3_comp, ref_Ti2N2O_comp, ref_Va_comp]
    ).T
    end_state_energies = np.array(
        [ref_Ti_energy, ref_Ti4NO3_energy, ref_Ti2N2O_energy, ref_Va_energy]
    )
    formation_energy_calculator = FormationEnergyCalculator(
        end_state_compositions, end_state_energies
    )
    formation_energies = formation_energy_calculator.get_formation_energy(
        points=comp, energies=energies
    )
    # passes
    assert np.all(
        np.isclose(formation_energies - true_formation_energies, 0, atol=1e-6)
    )
