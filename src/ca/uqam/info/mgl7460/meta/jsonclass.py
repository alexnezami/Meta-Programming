from io import TextIOWrapper
import importlib
import inspect

from ca.uqam.info.mgl7460.meta.relationship import Relationship


class JSONClass:

    # a dictionary of JSON classes, indexed by fully qualified class name
    JSON_CLASSES = dict()

    # creates an instance of a JSONClass, and adds it to the JSON_CLASSES global
    # dictionary, indexed by fully qualified name
    def __init__(self, name: str, package: str):
        self.name = name
        self.package = package
        self.attributes = dict()
        self.relationships = dict()
        self.type = None
        self.generated_class_file_name= None
        JSONClass.JSON_CLASSES[self.name] = self

    def fully_qualified_name(self):
        return self.package + "." + self.name

    def add_attribute(self, attributeName: str, valueType=object)-> None:
        self.attributes[attributeName]=valueType


    # # this method 
    # def set_attribute_value(self, receiver: object, attribute_name: str, attribute_value: object):        
    #     if attribute_name in self.attributes:
    #         #J'ai utilisé la fonction setattr par défaut de python pour modifier les valeurs des propriétés d'un objet au moment de l'exécution.
    #         #Ceci est très utile dans les cas où le nom de la propriété n'est pas connu au moment de l'écriture du code
    #         #et doit être spécifié au moment de l'exécution.
    #         setattr(receiver, attribute_name, attribute_value)
    #     else:
    #         # Si on n'a pas trouvé attribute_name dans    attributes , on diffuse un message erreur
    #         raise AttributeError(f"{attribute_name} n'a pas trouvé en classe {self.name}")



    # Adds a relationship from the current class to an entity named target_type_name
    def add_relationship(self, relation_name: str, target_type_name: str, multiplicity: int, index_field: str = None):
        relationship = Relationship(relation_name,self.name, target_type_name, multiplicity, index_field)
        self.add_relationship_object(relationship)

    def add_relationship_object(self, relationship):
        self.relationships[relationship.name] =relationship

    def __str__(self) -> str:
        display_string = self.name +"\n"
        display_string = display_string + "\tAttributs:\n"
        for att_name in iter(self.attributes):
            display_string = display_string + "\t\t" + att_name + " :" + self.attributes.get(att_name)+ "\n"
        
        display_string = display_string + "\tRelations:\n"
        for relation_name in iter(self.relationships):
            display_string = display_string + "\t\t" + self.relationships.get(relation_name).__str__() + "\n"
        return display_string
    
    # This method generates the code for this (self) JSONClass object.
    # 
    # If the class refers to user classes, and those have not been generated
    # yet, they are recursively generated and imported
    def generate_code(self, output_path: str):
        file_name = output_path + "/" + self.name + ".py"
        # 1. open the file
        python_file = open(file_name,'w+')

        # 2. print class header
        python_file.write("class " + self.name + ":\n")

        # 3. generate constructor
        self.generate_constructor(python_file)

        # 4. generate accessors
        self.generate_accessors(python_file)

        # 5. generate __str__ method
        self.generate__str__method(python_file)

        # 6. close the file
        python_file.close()

        # 7. mark the class as having been generated, by
        # specifying the name of the code file
        self.generated_class_file_name= file_name

    # 
    # This method loads the code for this (self) JSONClass object,
    # and returns the corresponding type.
    # 
    def load_code(self):
        # 1. First check whether the code was generated. 
        # if not, it returns None

        if (self.generated_class_file_name == None):
            return None
        
        # 2. now, load the corresponding module
        module = importlib.import_module(self.fully_qualified_name())
        print("The module is: " + module.__str__())

        # 3. get the 'type' object that represents the 'compiled version'
        #    of this JSONClass. I called it class_class_object in my code
        #    
        class_class_object = module.__dict__[self.name]
        self.type = class_class_object    
     
        return self.type

    # By default, the constructor will take a value for each attribute, and initialize it.
    # It will also initialize ONE_TO_MANY relationships to en empty collection
    # of whichever structure is appropriate: a) a list, or b) a map (if the relationship
    # is indexed)
    def generate_constructor(self, python_file: TextIOWrapper):
        # Démarrer la définition du constructeur
        attribute_names = ", ".join(self.attributes.keys())
        python_file.write(f"def __init__(self, {attribute_names}):\n")

        #parameter_list = ", ".join(["self"] + list(self.attributes.keys()))
        #constructor_signature = f"\tdef __init__({parameter_list}):\n"
        #python_file.write(constructor_signature)
    
        # Initialiser chaque attribut
        for attributename in iter(self.attributes.keys()):
            python_file.write(f"\t\tself.{attributename} = {attributename}\n")

        # Initialiser les relations
        for relation in self.relationships.values():
            if relation.multiplicity == Relationship.ONE_TO_ONE:
                python_file.write(f"\t\tself.{relation.name} = None\n")
            else:
                container_type = "dict" if relation.is_indexed() else "list"
                python_file.write(f"\t\tself.{relation.name} = {container_type}()\n")
    
        python_file.write("\n\n")    

    #
    # This method generates the __str__ method. it simply prints
    # the attributes and relationships of the object. It will
    # descend recursively if each object in the object tree
    # has a customer __str__() methods that prints its
    # fields
    #         
    def generate__str__method(self, python_file: TextIOWrapper):
        python_file.write("    def __str__(self) -> str:\n")
        python_file.write("        return f'{self.__class__.__name__}:' + '\\n' + \\\n")

        # Les attributs
        for attr_name in self.attributes:
            python_file.write(f"            f'{attr_name}: {getattr(self, attr_name)}' + '\\n' + \\\n")
        
        # Des relations
        for relation in iter(self.relationships.values()):

            python_file.write(f"            f'{relation}: {getattr(self, relation)}' + '\\n' )")

        python_file.write("\"\n") 



    #
    # This method generates accessors for collection-like attributes, i.e. ONE_TO_MANY
    # (indexed or not) relationships. For those, we need to provide methods to add,
    # remove, and iterate
    #         
    def generate_accessors(self, python_file: TextIOWrapper):
        # Iterate over the relationships
        for relation_name in iter(self.relationships.keys()):
            relation = self.relationships[relation_name]

            # 1. generate adder
            adder_string = self.get_adder_string(relation_name,relation)
            python_file.write(adder_string)

            # 2. generate remover
            remover_string = self.get_remover_string(relation_name,relation)
            python_file.write(remover_string)

            # 3. generate iterator
            iterator_string = self.get_iterator_string(relation_name,relation)
            python_file.write(iterator_string)

            # 4. generate indexed accerssor, if relation is indexed
            if (relation.index_field != None):
                indexed_accessor_string = self.get_indexed_accessor_string(relation_name,relation)
                python_file.write(indexed_accessor_string)
            

    # on crée une chaîne de code pour ajouter des éléments à une relation
    def get_adder_string(self, relation_name: str, relation: Relationship)-> str:
        if relation.index_field:
            return f"""    def add_{relation_name}(self, item):
        self.{relation_name}[item.{relation.index_field}] = item\n\n"""
        else:
            return f"""    def add_{relation_name}(self, item):
        self.{relation_name}.append(item)\n\n"""

    # on crée une chaîne de code pour supprimer des éléments d'une relation
    def get_remover_string(self, relation_name: str, relation: Relationship)-> str:
        if relation.index_field:
            return f"""    def remove_{relation_name}(self, item):
        self.{relation_name}.pop(item.{relation.index_field})\n\n"""
        else:
            return f"""    def remove_{relation_name}(self, item):
        self.{relation_name}.remove(item)\n\n"""

    # on renvoie une chaîne de code pour créer un itérateur pour la relation
    def get_iterator_string(self, relation_name: str, relation: Relationship)-> str:
        if relation.index_field:
            return f"""    def iter_{relation_name}(self):
        return iter(self.{relation_name}.values())\n\n"""
        else:
            return f"""    def iter_{relation_name}(self):
        return iter(self.{relation_name})\n\n"""

    # on crée une chaîne de code pour accéder aux éléments d'une relation indexée
    def get_indexed_accessor_string(self, relation_name: str, relation: Relationship)-> str:
        if relation.index_field:
            return f"""    def get_{relation_name}(self, key):
        return self.{relation_name}.get(key)\n\n"""
        else:
            return ""

    # on cree objet avec les donnees qu'on a deja trouve
    def create_object(self, json_fragment: dict):

        # on a cree un instance 
        new_obj = self.type({attr:json_fragment.get(attr) for attr in self.attributes})


        # traiter sur relation
        for name, relation in self.relationships.items():
            value = json_fragment.get(name)
            # si relation est indexe on cree une dictionaire
            if (relation.is_indexed()):

                relation_objects = {
                    key: JSONClass.JSON_CLASSES[relation.destination_entity].create_object(item)
                    for key, item in value.item()
                }
            else:
            # sinon on cree une list
                relation_objects = [
                    JSONClass.JSON_CLASSES[relation.destination_entity].create_object(item)
                    for item in value
                ]
            setattr(new_obj, name, relation_objects)

            return new_obj