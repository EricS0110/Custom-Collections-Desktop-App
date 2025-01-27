import customtkinter
from customtkinter import CTkFont

from src.security import load_settings

APP_TITLE = "Collection Manager"
APP_GEOMETRY = "900x800"


class WelcomeFrame(customtkinter.CTkFrame):
    def __init__(self, master, settings, **kwargs):
        super().__init__(master, **kwargs)
        self.heading_label = customtkinter.CTkLabel(
            self,
            text=f"Welcome to the {APP_TITLE} application",
            font=CTkFont(family="Arial", size=24, weight="bold", underline=True),
        )
        self.heading_label.grid(row=0, column=0, sticky="n", padx=10, pady=10)
        main_body_text = """
        This app will help you manage what items are stored in your MongoDB collection.


        Tabs:

        - Welcome: This tab

        - Settings: Application settings (not persistent)

        - New Collection: Create a new collection

        - Add One: Add one item to the collection

        - Add Bulk: Add multiple items to the collection

        - Download: Download a collection as an Excel file

        - Search: Search for items in the collection

        - Delete: Delete items from the collection
        """
        self.main_body_label = customtkinter.CTkLabel(
            self, text=main_body_text, font=CTkFont(family="Arial", size=16), anchor="w", justify="left"
        )
        self.main_body_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

        at_a_glance_text = f"""
        Database: {settings.mongo_database}
        """
        for key, value in settings.mongo_connection.summarize_collection_counts().items():
            at_a_glance_text += f"\n\t{key}: {value}"
        self.at_a_glance_label = customtkinter.CTkLabel(
            self, text=at_a_glance_text, font=("Arial", 16), anchor="w", justify="left"
        )
        self.at_a_glance_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)


class DarkModeToggleFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        def switch_event():
            if self.switch_var.get() == "on":
                customtkinter.set_appearance_mode("dark")
            elif self.switch_var.get() == "off":
                customtkinter.set_appearance_mode("light")

        self.switch_var = customtkinter.StringVar(value="on")
        self.dark_mode_toggle = customtkinter.CTkSwitch(
            master, text="Dark Mode", command=switch_event, variable=self.switch_var, onvalue="on", offvalue="off"
        )
        self.dark_mode_toggle.pack(side="top", padx=10, pady=10)


class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, master, settings, **kwargs):
        super().__init__(master, **kwargs)
        self.dark_mode_toggle_frame = DarkModeToggleFrame(self)
        self.dark_mode_toggle_frame.pack(side="top", anchor="w", expand=True, fill="both")


class NewCollectionFrame(customtkinter.CTkFrame):
    def __init__(self, master, settings, **kwargs):
        super().__init__(master, **kwargs)

        def create_collection():
            collection_name = self.collection_name_entry.get()
            if collection_name == "":
                return
            try:
                settings.mongo_connection.add_collection(collection_name)
            except Exception as e:
                import tkinter as tk
                from tkinter import messagebox

                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(title="Error", message=f"Error creating collection: {e}\n\nIt may already exist.")
                root.destroy()
            self.collection_name_entry.delete(0, "end")
            self.collections = settings.mongo_connection.list_collection_names()
            self.collection_list.configure(text=", ".join(self.collections))
            return

        self.heading_label = customtkinter.CTkLabel(
            self, text="Create a new collection", font=CTkFont(family="Arial", size=24, weight="bold", underline=True)
        )
        self.heading_label.grid(row=0, column=0, sticky="n", padx=10, pady=10)
        self.collection_name_label = customtkinter.CTkLabel(self, text="Collection Name:")
        self.collection_name_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.collection_name_entry = customtkinter.CTkEntry(self)
        self.collection_name_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        self.create_collection_button = customtkinter.CTkButton(
            self, text="Create Collection", command=create_collection
        )
        self.create_collection_button.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        # Add a list of the current collections for the user and a button to refresh the list
        self.collection_list_label = customtkinter.CTkLabel(self, text="Current Collections:")
        self.collection_list_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.collection_list = customtkinter.CTkLabel(self)
        self.collection_list.grid(row=3, column=1, sticky="w", padx=10, pady=10)
        self.collections = settings.mongo_connection.list_collection_names()
        self.collection_list.configure(text=", ".join(self.collections))

        def refresh_list():
            self.collections = settings.mongo_connection.list_collection_names()
            self.collection_list.configure(text=", ".join(self.collections))
            return

        self.refresh_button = customtkinter.CTkButton(self, text="Refresh List", command=refresh_list)
        self.refresh_button.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=10)


class CollectionsDropdownWithAllFrame(customtkinter.CTkFrame):
    def __init__(self, master, settings, **kwargs):
        super().__init__(master, **kwargs)
        self.collection_label = customtkinter.CTkLabel(self, text="Collection:")
        self.collection_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.collection_dropdown = customtkinter.CTkComboBox(
            self, values=["All"] + settings.mongo_connection.list_collection_names()
        )
        self.collection_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=10)


class AddOneFrame(customtkinter.CTkFrame):
    """
    Frame for adding a single item to a collection. Populate the currently available fields for all documents in the selected collection.
    Update the available fields when the collection is changed to reflect the new collection's fields.
    """

    def __init__(self, master, settings, **kwargs):
        super().__init__(master, **kwargs)
        self.settings = settings
        self.collection_label = customtkinter.CTkLabel(self, text="Collection:")
        self.collection_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.collection_dropdown = customtkinter.CTkComboBox(
            self, values=settings.mongo_connection.list_collection_names(), command=self.refresh_fields
        )
        self.collection_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        self.fields_frame = customtkinter.CTkFrame(self)
        self.fields_frame.grid(row=1, column=0, sticky="w", padx=10, pady=10, columnspan=2)

        self.create_fields()

        # Add a button to preview the item to the collection based on the fields and values entered by the user
        self.preview_item_button = customtkinter.CTkButton(self, text="Add Item", command=self.preview_item)
        self.preview_item_button.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        # Add a label in column 2 to display a preview of the item to be added
        # based on the available fields and values entered by the user
        self.preview_label = customtkinter.CTkLabel(self, text="Preview:")
        self.preview_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.preview_text = customtkinter.CTkTextbox(self, width=40, height=10)
        self.preview_text.grid(row=3, column=1, sticky="w", padx=10, pady=10)

    def create_fields(self):
        collection_name = self.collection_dropdown.get()
        if not collection_name:
            return
        fields = self.settings.mongo_connection.list_field_names(collection_name)
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        try:
            for i, field in enumerate(fields):
                label = customtkinter.CTkLabel(self.fields_frame, text=field)
                label.grid(
                    row=i,
                    column=0,
                    sticky="w",
                    padx=10,
                    pady=5,
                )
                entry = customtkinter.CTkEntry(self.fields_frame)
                entry.grid(row=i, column=1, sticky="w", padx=10, pady=5)
        except TypeError:
            pass

    def refresh_fields(self, event=None):
        self.create_fields()

    def preview_item(self):
        """
        Preview the item to be added to the collection based on the fields and values entered by the user
        :return: None
        """
        item = {}
        for widget in self.fields_frame.winfo_children():
            if isinstance(widget, customtkinter.CTkEntry):
                item[widget.cget("text")] = widget.get()
        self.preview_text.configure(text=str(item))
        return


class MainTabView(customtkinter.CTkTabview):
    def __init__(self, master, settings, **kwargs):
        super().__init__(master, **kwargs)
        self.add("    Welcome    ")
        self.add("    Settings    ")
        self.add("    New Collection    ")
        self.add("    Add One    ")
        self.add("    Add Bulk    ")
        self.add("    Download    ")
        self.add("    Search    ")
        self.add("    Delete    ")

        self.welcome_frame = WelcomeFrame(master=self.tab("    Welcome    "), settings=settings)
        self.welcome_frame.pack(anchor="w", expand=True, fill="both")
        self.settings_frame = SettingsFrame(master=self.tab("    Settings    "), settings=settings)
        self.settings_frame.pack(anchor="w", expand=True, fill="both")
        self.settings_frame = NewCollectionFrame(master=self.tab("    New Collection    "), settings=settings)
        self.settings_frame.pack(anchor="w", expand=True, fill="both")
        self.add_one_frame = AddOneFrame(master=self.tab("    Add One    "), settings=settings)
        self.add_one_frame.pack(anchor="w", expand=True, fill="both")


class App(customtkinter.CTk):
    def __init__(self, settings):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)

        self.main_tab_view = MainTabView(self, settings=settings)
        self.main_tab_view.pack(anchor="e", expand=True, fill="both")


if __name__ == "__main__":
    main_settings = load_settings()
    app = App(settings=main_settings)
    app.mainloop()
