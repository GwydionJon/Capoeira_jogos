from jogos_app import jogosApp
import paths


def main():
    app = jogosApp().app

    app.run_server(debug=True, use_reloader=True, port=8051)


if __name__ == "__main__":
    main()
