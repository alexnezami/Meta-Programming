class produit:
def __init__(self, id, nom, description, prixUnitaire):
		self.id = id
		self.nom = nom
		self.description = description
		self.prixUnitaire = prixUnitaire


    def __str__(self) -> str:
        return f'{self.__class__.__name__}:' + '\n' + \
