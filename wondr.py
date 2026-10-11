
import os
import json
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text
from rich.align import Align
from rich import box

load_dotenv(os.path.expanduser("~/wondr/.env"))

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
HISTORY_FILE = os.path.expanduser("~/wondr/history.json")

console = Console()
history = []


def load_history():
    global history
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []


def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=2)


def show_header():
    console.clear()
    logo = Text()
    logo.append("W", style="bold bright_cyan")
    logo.append("ONDR", style="bold white")
    logo.append("\nVotre assistant IA personnel", style="dim white")

    console.print()
    console.print(Align.center(logo))
    console.print()
    console.print(
        Panel(
            f"[bright_cyan]Modèle[/bright_cyan]  {MODEL}\n"
            "[bright_cyan]Statut[/bright_cyan]  Assistant prêt\n"
            "[bright_cyan]Commandes[/bright_cyan]  /help · /history · /clear · /exit",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def ask_gemini(question):
    global history

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODEL}:generateContent"
    )

    contents = []
    for item in history[-12:]:
        contents.append({
            "role": item["role"],
            "parts": [{"text": item["text"]}],
        })

    contents.append({
        "role": "user",
        "parts": [{"text": question}],
    })

    payload = {
        "systemInstruction": {
            "parts": [{
                "text": (
                    "Tu es Wondr, un assistant IA utile, intelligent et "
                    "honnête. Réponds en français par défaut, clairement, "
                    "avec une mise en forme lisible. Si tu ne sais pas, "
                    "dis-le. Ne prétends pas avoir effectué une action "
                    "que tu n'as pas réellement faite."
                )
            }]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        },
    }

    try:
        with console.status(
            "[bright_cyan]Wondr réfléchit...[/bright_cyan]",
            spinner="dots",
        ):
            response = requests.post(
                url,
                params={"key": API_KEY},
                json=payload,
                timeout=60,
            )

        if not response.ok:
            try:
                detail = response.json()["error"]["message"]
            except (ValueError, KeyError, TypeError):
                detail = response.text[:300]
            console.print(
                Panel(
                    f"[red]Erreur API : {detail}[/red]",
                    border_style="red",
                )
            )
            return

        data = response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]

        console.print(
            Panel(
                Markdown(answer),
                title="[bold bright_cyan]WONDR[/bold bright_cyan]",
                border_style="bright_cyan",
                padding=(1, 2),
                box=box.ROUNDED,
            )
        )

        history.append({"role": "user", "text": question})
        history.append({"role": "model", "text": answer})
        save_history()

    except requests.Timeout:
        console.print("[red]La requête a pris trop de temps. Réessaie.[/red]")
    except requests.RequestException as error:
        console.print(f"[red]Erreur réseau : {error}[/red]")
    except (KeyError, IndexError, TypeError, ValueError):
        console.print(
            "[red]Réponse inattendue de l'API. Vérifie le modèle et ta clé.[/red]"
        )


def main():
    if not API_KEY:
        console.print(
            "[red]Clé API introuvable. Vérifie ~/wondr/.env[/red]"
        )
        return

    load_history()
    show_header()

    while True:
        try:
            question = Prompt.ask("[bold bright_cyan]Toi[/bold bright_cyan]").strip()

            if not question:
                continue

            if question == "/exit":
                console.print("[dim]À bientôt ![/dim]")
                break

            elif question == "/help":
                console.print(Panel(
                    "/help     Afficher les commandes\n"
                    "/history  Afficher les derniers échanges\n"
                    "/clear    Effacer l'historique enregistré\n"
                    "/model    Afficher le modèle utilisé\n"
                    "/exit     Quitter Wondr",
                    title="Commandes",
                    border_style="bright_cyan",
                ))

            elif question == "/history":
                if not history:
                    console.print("[dim]Aucun échange enregistré.[/dim]")
                else:
                    for item in history[-10:]:
                        label = "Toi" if item["role"] == "user" else "Wondr"
                        console.print(
                            f"[bright_cyan]{label}[/bright_cyan] "
                            f"{item['text'][:500]}"
                        )

            elif question == "/clear":
                history.clear()
                save_history()
                console.print("[green]Historique effacé.[/green]")

            elif question == "/model":
                console.print(f"[bright_cyan]Modèle : {MODEL}[/bright_cyan]")

            else:
                ask_gemini(question)

        except KeyboardInterrupt:
            console.print("\n[dim]Utilise /exit pour quitter.[/dim]")
        except EOFError:
            break


if __name__ == "__main__":
    main()

