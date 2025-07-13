import tkinter as tk
from tkinter import Toplevel, simpledialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mpimg
import src.database as db

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Fashion Design Software")
        self.master.geometry("800x600")
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # Drawing Canvas
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        # Tool selection
        self.tool_frame = tk.Frame(self)
        self.tool_frame.pack(side="top", fill="x")

        self.line_button = tk.Button(self.tool_frame, text="Line", command=self.select_line_tool)
        self.line_button.pack(side="left")

        self.save_button = tk.Button(self.tool_frame, text="Save", command=self.save_canvas)
        self.save_button.pack(side="left")

        self.open_button = tk.Button(self.tool_frame, text="Open", command=self.open_canvas)
        self.open_button.pack(side="left")

        self.curve_button = tk.Button(self.tool_frame, text="Curve", command=self.select_curve_tool)
        self.curve_button.pack(side="left")

        self.preview_3d_button = tk.Button(self.tool_frame, text="3D Preview", command=self.show_3d_preview)
        self.preview_3d_button.pack(side="left")

        self.fabric_db_button = tk.Button(self.tool_frame, text="Fabric Database", command=self.show_fabric_db)
        self.fabric_db_button.pack(side="left")

        # Quit Button
        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def save_canvas(self):
        self.canvas.postscript(file="pattern.ps", colormode='color')

    def open_canvas(self):
        # This is a bit tricky, as we can't directly load the postscript back as editable objects.
        # For now, we will clear the canvas and draw the postscript file as an image.
        # A more advanced implementation would be needed to truly "open" and edit the file.
        self.canvas.delete("all")
        try:
            self.canvas.image = tk.PhotoImage(file="pattern.ps")
            self.canvas.create_image(0, 0, image=self.canvas.image, anchor="nw")
        except tk.TclError:
            print("Could not open pattern.ps. Make sure you have Ghostscript installed.")

    def select_line_tool(self):
        self.canvas.bind("<Button-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.draw_line)

    def select_curve_tool(self):
        self.canvas.bind("<Button-1>", self.start_curve)
        self.curve_points = []

    def start_curve(self, event):
        self.curve_points.append((event.x, event.y))
        if len(self.curve_points) == 4:
            self.canvas.create_line(self.curve_points, smooth=True)
            self.curve_points = []

    def show_fabric_db(self):
        self.db_window = Toplevel(self.master)
        self.db_window.title("Fabric Database")

        self.fabrics_list = tk.Listbox(self.db_window)
        self.fabrics_list.pack(side="top", fill="both", expand=True)

        self.refresh_fabrics_list()

        add_button = tk.Button(self.db_window, text="Add Fabric", command=self.add_fabric_entry)
        add_button.pack(side="bottom")

    def refresh_fabrics_list(self):
        self.fabrics_list.delete(0, tk.END)
        conn = db.create_connection()
        if conn:
            fabrics = db.get_all_fabrics(conn)
            for fabric in fabrics:
                self.fabrics_list.insert(tk.END, f"ID: {fabric[0]}, Name: {fabric[1]}, Color: {fabric[2]}")
            conn.close()

    def add_fabric_entry(self):
        name = simpledialog.askstring("Input", "Enter fabric name:", parent=self.db_window)
        color = simpledialog.askstring("Input", "Enter fabric color:", parent=self.db_window)
        if name and color:
            conn = db.create_connection()
            if conn:
                db.add_fabric(conn, (name, color))
                conn.close()
                self.refresh_fabrics_list()
                messagebox.showinfo("Success", "Fabric added successfully.", parent=self.db_window)

    def show_3d_preview(self):
        preview_window = Toplevel(self.master)
        preview_window.title("3D Preview")

        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111, projection='3d')

        try:
            # Convert the postscript file to a png image first
            # This requires ghostscript to be installed
            from PIL import Image
            img = Image.open("pattern.ps")
            img.save("pattern.png")

            img = mpimg.imread("pattern.png")
            x, y = range(img.shape[1]), range(img.shape[0])
            X, Y = self.meshgrid_compatible(x,y)
            ax.plot_surface(X, Y, 0, rstride=10, cstride=10, facecolors=img)
        except Exception as e:
            print(f"Could not generate 3D preview: {e}")
            print("Please ensure you have Ghostscript and Pillow installed.")
            ax.text2D(0.5, 0.5, "Could not generate 3D preview.", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)


        canvas = FigureCanvasTkAgg(fig, master=preview_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def meshgrid_compatible(self,x, y):
        import numpy as np
        X, Y = np.meshgrid(x, y)
        return X, Y


    def start_line(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def draw_line(self, event):
        if self.start_x and self.start_y:
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y)
            self.start_x = event.x
            self.start_y = event.y

if __name__ == "__main__":
    db.main()
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
