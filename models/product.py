from utils.db import SupabaseClient


class Product:
    def __init__(self, data=None, name=None):
        if name is not None:
            data = SupabaseClient().read(
                table="products", query_key="name", query_value=name
            )
            if not data:
                raise Exception("There is no product with name = ", name)
            else:
                # Assuming is_unique constraint on name in Products table
                data = data[0]
        # Name of the product
        self.name = data["name"]
        # Description of the product
        self.desc = data["description"]
        # Organisation associated with the product
        self.org = data["organisation"]
        # The wili page url for the product on C4GT github
        self.wiki_url = data["wiki_url"]
        # Projects under this product
        self.projects = data["projects"]
        # Mentors assigned to projects associated with this product
        self.mentors = data["mentors"] if data["mentors"] else []
        # Contributors assigned to projects under this product
        self.contributers = data["contributors"] if data["contributors"] else []
        # discord channel id of the dedicated discord channel for this Product
        self.channel = data["channel"]

    @classmethod
    def is_product(cls, product_name):
        db_client = SupabaseClient()
        data = db_client.read(
            table="products", query_key="name", query_value=product_name
        )
        if len(data) == 1:
            return True
        if len(data) > 1:
            raise Exception(
                "Product name should be unique but recieved multiple items for this name."
            )
        return False

    @classmethod
    def get_all_products(cls):
        db_client = SupabaseClient()
        data = db_client.read_all(table="products")
        return data

    def assign_channel(self, discord_id):
        SupabaseClient().update(
            table="products",
            update={"channel": discord_id},
            query_key="name",
            query_value=self.name,
        )
        return
