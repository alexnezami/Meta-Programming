class commande:
	def __init__(self, id):
		self.id = id
		self.table_ligne_commandes = dict()


    def add_table_ligne_commandes(self, item):
        self.table_ligne_commandes[item.dict_keys(['id_produit', 'quantite'])] = item

    def remove_table_ligne_commandes(self, item):
        self.table_ligne_commandes.pop(item.dict_keys(['id_produit', 'quantite']))

    def iter_table_ligne_commandes(self):
        return iter(self.table_ligne_commandes.values())

    def get_table_ligne_commandes(self, key):
        return self.table_ligne_commandes.get(key)

