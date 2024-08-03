from models.circuit import Circuit


class MotoGpParser:
    
    @staticmethod
    def parse_circuit(json: dict) -> Circuit:
        return Circuit(
            0,
            json['circuit']['id'],
            json['circuit']['name'],
            json['circuit']['iso_code'],
            None,
            None,
            None,
            None
        )