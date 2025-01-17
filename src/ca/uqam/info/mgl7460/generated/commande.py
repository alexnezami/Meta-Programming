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

	def __str__(self) -> str:
		return_string = "commande["
		return_string = return_string + "id = "+ self.id.__str__()+ ", "
		relation_str_ = "table_ligne_commandes" + " = ["
		relation_str_ = relation_str_[:-2] + "]"
		return_string = return_string + relation_str_ + ", "
		return_string = return_string[:-2] + "]"
		return return_string
