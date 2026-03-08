from rich.text import Text

from textual.app import App
from textual import events, on
from textual.binding import Binding
from textual.widgets import Button, Header, Label, Footer, Input, DataTable, Rule
from textual.containers import Horizontal, VerticalGroup
from textual.screen import ModalScreen

from utils import *
from validators import InputeValidator

class UserManagement(App):

    TITLE = "User Management"
    SUB_TITLE = "System User Management Utility Tool"

    CSS_PATH = "./style.tcss"

    BINDINGS = [
        Binding(key="a", action="add_user", description="Add A New User"),
        Binding(key="delete", action="delete_user", description="Delete a User"),
        Binding(key="ctrl+d", action="delete_group", description="Delete a Group"),
        Binding(key="l", action="lock_user", description="Un/Lock User"),
        Binding(key="p", action="change_password", description="Change password"),
        Binding(key="i", action="", description="Info"),
        Binding(key="j", action="down", description="Scroll down", show=False),
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        ),
    ]

    def compose(self):
        yield Header()
        with VerticalGroup(id="users-container"):
            with Horizontal(classes="h"):
                yield Label("User Management:")
                yield Button("Add User", id="add-user", variant="primary")
                # yield Button("Delete User", id="del-user", variant="error")
            yield DataTable(id="users")
        yield Rule(orientation="vertical", line_style="dashed")
        with VerticalGroup(id="groups-container"):
            with Horizontal(classes="h"):
                yield Label("Group Management:")
                yield Button("Add Group", id="add-group", variant="primary")
                # yield Button("Delete Group", id="del-group", variant="error")
            yield DataTable(id="groups")
        yield Footer()

    def on_mount(self):
        utable = self.query_one("#users", DataTable)
        utable.cursor_type = "row"
        utable.zebra_stripes = True
        utable.add_columns(*list_users()[0])

        gtable = self.query_one("#groups", DataTable)
        gtable.cursor_type = "row"
        gtable.zebra_stripes = True
        gtable.add_columns(*list_groups()[0])
        self.populate_tables()

    def populate_tables(self, *args):
        utable = self.query_one("#users", DataTable)
        utable.clear()
        for row in list_users()[1:]:
            styled = (
                Text(str(cell), style="italic", justify="center") for cell in row
            )
            utable.add_row(*styled)

        gtable = self.query_one("#groups", DataTable)
        gtable.clear()
        for row in list_groups()[1:]:
            styled = (
                Text(str(cell), style="italic", justify="center") for cell in row
            )
            gtable.add_row(*styled)

    def action_add_user(self):
        self.add_user()

    def action_delete_user(self):
        utable = self.query_one("#users", DataTable)
        row_idx = utable.cursor_row
        if row_idx == None:
            return
        
        user = utable.get_row_at(row_idx)[0]

        re = delete_user(str(user))
        if re[0] == -1:
                self.notify(re[1], severity="error")
        else:
            self.notify("User Deleted Successfully!", title="Success")
            self.populate_tables()
            return

    def action_delete_group(self):
        gtable = self.query_one("#groups", DataTable)
        row_idx = gtable.cursor_row
        if row_idx == None:
            return
        
        g = gtable.get_row_at(row_idx)[0]

        re = delete_group(str(g))
        if re[0] == -1:
                self.notify(re[1], severity="error")
        else:
            self.notify("Group Deleted Successfully!", title="Success")
            self.populate_tables()
            return

    def action_lock_user(self):
        pass

    def action_change_password(self):
        pass

    @on(Button.Pressed,'#add-user')
    def add_user(self):
        self.push_screen(AddUserScreen(), callback=self.populate_tables)

    @on(Button.Pressed,'#add-group')
    def add_group(self):
        self.push_screen(AddGroupScreen(), callback=self.populate_tables)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row = event.row_key
        data = event.control.get_row(row)
        fields = event.control.get_row_at(0)
        self.push_screen(ModifyEntryScreen(fields, data))  # push new screen

    def on_key_pressed(self, event: events.Key):
        pass



class ModifyEntryScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    def __init__(self, fields, data):
        super().__init__()
        self.fields = fields
        self.data = data

    def compose(self):
        yield Label("Edit Row")
        with Horizontal():
            yield Button("Ok!", id="ok", variant="success")
            yield Button("Delete", id="delete", variant="error")
            yield Button("Cancel", id="cancel", variant="warning")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.app.pop_screen()

class AddUserScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    def compose(self):
        yield Label("Add User:", classes="buttons-group")
        yield Input(placeholder="Username", validators=[
            InputeValidator()
        ], id="username")
        yield Input(placeholder="Full Name", validators=[
            InputeValidator()
        ], id="full-name")
        yield Input(placeholder="Password", id="pass", validators=[
            InputeValidator(less_count=6)
        ], password=True)
        yield Input(placeholder="Confirm Password",id="confirm-pass", validators=[
            InputeValidator(less_count=6)
        ], password=True)
        with Horizontal(classes="buttons-group"):
            yield Button("Ok!", id="ok", variant="success")
            yield Button("Cancel", id="cancel", variant="warning")

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed):
        if not event.validation_result.is_valid:
            self.notify(str(event.validation_result.failure_descriptions[0]), title="Not Valid", severity="error", timeout=2)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "ok":
            inputs = self.query(Input)
            all_valid = True
            values = []
            for inp in inputs:
                all_valid = inp.is_valid
                values.append(inp.value)

            if not all_valid:
                self.notify("Fix Problems With Input", title="Error", severity="error")
                return

            if values[-1] != values[-2]:
                self.notify("Password Doesn't Match", title="Error", severity="error")
                return
            
            # Call the make user function
            re = add_user(values[0], values[1], values[2])
            if re[0] == -1:
                self.notify(re[1], severity="error")
            else:
                self.app.notify("User Added Successfully!", title="Success")
                self.dismiss("refresh")
                return

class AddGroupScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    def compose(self):
        yield Label("Add Group:", classes="buttons-group")
        yield Input(placeholder="Group Name", validators=[
            InputeValidator()
        ], id="groupname")
        with Horizontal(classes="buttons-group"):
            yield Button("Ok!", id="ok", variant="success")
            yield Button("Cancel", id="cancel", variant="warning")

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed):
        if not event.validation_result.is_valid:
            self.notify(str(event.validation_result.failure_descriptions[0]), title="Not Valid", severity="error", timeout=2)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "ok":
            inputs = self.query(Input)
            all_valid = True
            values = []
            for inp in inputs:
                all_valid = inp.is_valid
                values.append(inp.value)

            if not all_valid:
                self.notify("Fix Problems With Input", title="Error", severity="error")
                return
            
            re = add_group(values[0])
            if re[0] == -1:
                self.notify(re[1], severity="error")
            else:
                self.app.notify("Group Added Successfully!", title="Success")
                self.dismiss("refresh")
                return

if __name__ == "__main__":
    UserManagement().run()