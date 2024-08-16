import json
import numpy as np
import libcasm.xtal as xtal
from libcasm.composition import (
    make_standard_origin_and_end_members,
    CompositionConverter,
    FormationEnergyCalculator
)

def test_binary():
    # read data
    with open('li_ag_bcc_relax_vasp_data.json', 'r') as f:
        data = json.load(f)
    true_formation_energies = np.array([i['formation_energy_per_atom'] for i in data.values()])
    energies = np.array([i['energy_per_atom'] for i in data.values()])
    comp = np.array([i['comp'] for i in data.values()]).reshape(1, -1)
    ref_Ag_energy = -2.717411600000
    ref_Li_energy = -1.904210800000

    # calculate formation energies
    end_state_compositions = np.array([[0, 1]]) # Li=0, Li=1
    end_state_energies = np.array([ref_Ag_energy, ref_Li_energy])
    formation_energy_calculator = FormationEnergyCalculator(
        end_state_compositions, end_state_energies
    )
    formation_energies = formation_energy_calculator.get_formation_energy(
        points=comp, energies=energies
    )
    assert np.all(np.isclose(formation_energies - true_formation_energies, 0), atol=1e-6)
    
    
