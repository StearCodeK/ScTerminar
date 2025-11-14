from controllers.product_controller import ProductController


def show_inventory(app):
    """Mostrar la gestión de inventario"""
    controller = ProductController(app)
    controller.show_inventory()
