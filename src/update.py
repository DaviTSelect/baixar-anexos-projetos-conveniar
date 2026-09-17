import customtkinter as ctk
import requests
import threading

class AutoupdaterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Checar novas atualizações")
        self.geometry("400x200")
        self.resizable(False, False)

        self.label = ctk.CTkLabel(self, text="Verificando atualizações...", font=ctk.CTkFont(size=16, weight="bold"))
        self.label.pack(pady=(50, 10))

        self.update_idletasks()
        self.after(1000, self.checando_novas_atualizacoes)
        
    def checando_novas_atualizacoes(self):
        self.label.configure(text="Procurando atualizações no github...")
        threading.Thread(target=self.verificar_atualizacoes_github).start()



    def verificar_atualizacoes_github(self):
        url = "https://api.github.com/repos/DaviTSelect/baixar-anexos-projetos-conveniar/releases/latest"
        response = requests.get(url)
        if response.status_code == 200:
            latest_release = response.json()
            # Aqui você pode adicionar a lógica para comparar a versão atual com a última versão
        else:
            # Tratar erro na requisição
            pass

if __name__ == "__main__":
    app = AutoupdaterApp()
    app.mainloop()


#self.label.configure(text="Nenhuma atualização encontrada.")
#self.update_idletasks()
#self.after(2000, self.destroy)