from capoeira_jogos.jogos_app import Jogos_App


app = Jogos_App().app
app.title = "capoeira jogos"

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True, port=8080)
