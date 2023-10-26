# ttk es la biblioteca que nos permite diseñar toda la interfaz
from tkinter import ttk
from tkinter import *

# sqlite3 es un modelo para conectarse a la base de datos
import sqlite3

class Product:
    db_name = 'database.db'
    
    def __init__(self, window):
        self.wind = window
        self.wind.title('Products Application') # Definimos el título de la app

        # Creating a Frame Container (un contenedor que permite tener elementos dentro)
        frame = LabelFrame(self.wind, text="Register a new product")
        # Acá posicionamos el elemento en la ventana (con el método grid)
        frame.grid(row = 0, column = 0, columnspan = 3, pady = 20)

        # Name input
        # Para que este label esté dentro del frame que creamos, hay que pasarle el nombre de la variable como parámetro al label
        Label(frame, text = "Name: ").grid(row = 1, column = 0)
        self.name = Entry(frame) # Entry() es para crear un input
        self.name.focus() # Esto es para que cuando se ejecute la app, le haga focus a ese campo (en este caso el input de name)
        self.name.grid(row = 1, column = 1)
        
        # Price input
        Label(frame, text = "Price: ").grid(row = 2, column = 0)
        self.price = Entry(frame)
        self.price.grid(row = 2, column = 1)

        # Button add product
        # Acá creamos el botón, que lleva como argumentos el lugar donde va a estar, el texto que va a tener, y la función que tendrá
        ttk.Button(frame, text = "Save product", command = self.add_products).grid(row = 3, columnspan = 2, sticky = W + E)

        # Output messages
        self.message = Label(text = "", fg = "red")
        self.message.grid(row = 3, column = 0, columnspan = 2, sticky = W + E)

        # Table
        # Para crear una tabla se utiliza ttk.Treeview, y se le pasa como argumentos las filas y las columnas
        self.tree = ttk.Treeview(height = 10, columns = 2)
        self.tree.grid(row = 4, column = 0, columnspan = 2)
        # heading (de la clase TreeView) sirve para ponerle un encabezado a una columna
        # Recibe 2 parámetros obligatorios: el id de la columna y el texto; en este caso tambíen tiene el 'anchor = CENTER' para que esté centrado
        self.tree.heading("#0", text = "Name", anchor = CENTER)
        self.tree.heading("#1", text = "Price", anchor = CENTER)

        # Buttons
        ttk.Button(text = 'DELETE', command = self.delete_products).grid(row = 5, column = 0, sticky = W + E)
        ttk.Button(text = 'EDIT', command = self.edit_products).grid(row = 5, column = 1, sticky = W + E)

        # Rellenando las filas de las tablas
        self.get_products()
    
    # Esta función es para ejecutar las consultas sql sin tener que repetir tanto código
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def get_products(self):
        # Estas 3 líneas de código son para limpiar la tabla si es que tiene algo
        records = self.tree.get_children() # get_children es para obtener todos los elementos o datos que estén dentro de la tabla
        for element in records:
            self.tree.delete(element)
        
        # Acá hacemos la consulta sql
        query = 'SELECT * FROM product ORDER BY name DESC'
        db_rows = self.run_query(query)
        
        # Aca rellenamos los datos
        for row in db_rows:
            self.tree.insert("", 0, text = row[1], values = row[2])

    def validation(self):
        return len(self.name.get()) != 0 and len(self.price.get()) != 0

    def add_products(self):
        if self.validation():
            query = 'INSERT INTO product VALUES(NULL, ?, ?)'
            parameters = (self.name.get(), self.price.get())
            self.run_query(query, parameters)
            self.message['text'] = "Product {} added successfully".format(self.name.get())
            self.name.delete(0, END)
            self.price.delete(0, END)
        else:
            self.message['text'] = "Name and Price are required"
        self.get_products()
        
    def delete_products(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Please select a Record'
            return
        self.message['text'] = ''
        name = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM product WHERE name = ?'
        self.run_query(query, (name, ))
        self.message['text'] = 'Record {} deleted successfully'.format(name)
        self.get_products()
        
    def edit_products(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Please select a Record'
            return
        name = self.tree.item(self.tree.selection())['text']
        old_price = self.tree.item(self.tree.selection())['values'][0]
        self.edit_wind = Toplevel() # TopLevel es para crear una ventana encima de la anterior
        self.edit_wind.title = 'Edit Product'

        # Old name
        Label(self.edit_wind, text = 'Old Name: ').grid(row = 0, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = name), state = 'readonly').grid(row = 0, column = 2)
        # New name
        Label(self.edit_wind, text = 'New Name: ').grid(row = 1, column = 1)
        new_name = Entry(self.edit_wind)
        new_name.grid(row = 1, column = 2)
        
        # Old price
        Label(self.edit_wind, text = 'Old Price: ').grid(row = 2, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_price), state = 'readonly').grid(row = 2, column = 2)
        # New price
        Label(self.edit_wind, text = 'New Price: ').grid(row = 3, column = 1)
        new_price = Entry(self.edit_wind)
        new_price.grid(row = 3, column = 2)
        
        Button(self.edit_wind, text = 'Update', command = lambda: self.edit_records(new_name.get(), name, new_price.get(), old_price)).grid(row = 4, column = 2, sticky = W)

    def edit_records(self, new_name, name, new_price, old_price):
        query = 'UPDATE product SET name = ?, price = ? WHERE name = ? AND price = ?'
        parameters = (new_name,new_price,name,old_price)
        self.run_query(query,parameters)
        self.edit_wind.destroy()
        self.message['text'] = "Record {} updated successfully".format(name)
        self.get_products()
        
if __name__ == '__main__': # Esto es para comprobar que este sea el archivo principal (__main__)
    window = Tk() # Definimos "window" como la ventana principal de nuestra app
    application = Product(window) # Instanciamos la clase pasandole la ventana que creamos como parámetro
    window.mainloop() # mainloop() indica a la interfaz que debe quedarse esperando a que el usuario haga algo