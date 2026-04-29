import tkinter as tk

root = tk.Tk()

root.title("My Tkinter Window")
root.geometry("300x200"
              )
greet = tk.Label(root, text="Hello, Tkinter!")
greet.pack(pady=20)

root.mainloop()