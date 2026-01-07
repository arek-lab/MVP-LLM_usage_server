from app.graph.chains.cv_data_model import CVData
from app.graph.state import State

def ask_for_data_acceptation(state: State) -> CVData | None:
  print("Zweryfikuj proszę informacje. Możesz wprowadzać zmiany, które będą uwzględnione w ostatecznym CV")
  
  cv_data_acceptance = ''
  while cv_data_acceptance not in ("t", "n"):
      cv_data_acceptance = input("Akceptacja finalnych danych do CV (T/N):\n").lower()
  if cv_data_acceptance == "t":
        cv_data_acceptance = True
  elif cv_data_acceptance == 'n': 
      cv_data_acceptance = False
  
  # to do - edycja
  if not cv_data_acceptance:
    eidted_data = input("Fakeowa edycja danych. Daj enter 😉")
      
  print(f"Ostatecznie użyte dane, to dane {"nie" if cv_data_acceptance else ''}zmodyfikowane")
  
  return eidted_data if not cv_data_acceptance else None