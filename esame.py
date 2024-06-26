import csv
from datetime import datetime

class ExamException(Exception):
    pass


class CSVTimeSeriesFile:
    def __init__(self, name):
        self.name = name
        self.can_read = True
        
        # Test per verificare che il file esista/sia apribile
        try:
            open_file = open(self.name, 'r')
            open_file.readline()
            
        except FileNotFoundError: 
            self.can_read = False
            raise ExamException(f'Il file {self.name} non esiste o non è leggibile!')

# get_data prende in input il file CSV e trasforma il contenuto in una lista di liste con ["data", numero di passeggeri] 
    def get_data(self):  
        data = [] # lista in cui verranno salvate le liste ["data", n_passengers]
        
        if not self.can_read:
            print('C''è stato un errore nell''apertura del file.')
            return None
        
        else: 
            
            with open(self.name, 'r') as file:
                open_file = csv.reader(file)
                prev_ts = None
                
                # Si creano delle tuple (indice, contenuto) con l'indice della riga su cui si sta lavorando e il rispettivo contenuto
                for i, line in enumerate(open_file):
                    
                    # Controlliamo che ci sia un'intestazione:
                    if i == 0:
                        try:
                            datetime.strptime(line[0], "%Y-%m") # Se si riesce a ricavare la data, allora non c'è un'intestazione
                        except ValueError:
                            continue # Se c'è, si salta la prima riga
                    
                    # Per ogni altra riga, si verifica se la riga sia vuota (not line) oppure se abbia meno di due elementi (quindi un campo vuoto):
                    if not line or len(line) < 2: 
                        continue 
                    
                    try:
                        date = line[0]
                        date = datetime.strptime(date, "%Y-%m")
                        # print(date)
                        
                        n_passengers = int(line[1])

                        # Gestione delle eccezioni e warning sui contenuti del file csv:
                        if prev_ts is not None and date < prev_ts: # Timestamp mal ordinato
                            raise ExamException(f'Il timestamp {date.strftime('%Y-%m')} è fuori ordine!')
                    
                        elif prev_ts is not None and date == prev_ts: # Timestamp duplicato
                            raise ExamException(f'Il timestamp {date.strftime('%Y-%m')} è duplicato!')
                        
                        elif date >= datetime.today(): # Timestamp che indica una data futura?
                            print('Warning: è stata inserita una data del futuro?!')
                            
                        prev_ts = date

                        # Se i dati contenuti nella riga erano corretti, si ritrasforma la data in stringa e si salva la lista:
                        date = date.strftime("%Y-%m")
                        data.append([date, n_passengers])
                    
                    except ValueError:
                        continue # Se il numero di passeggeri non è un intero positivo (o qualsiasi altra cosa), si salta e si continua senza sollevare eccezioni
                        
        return data
            
    
def detect_similar_monthly_variations(time_series, years):
    
    # 1. Gli input devono essere validi:
    # Si controlla che la lista di anni fornita sia corretta
    
    if not isinstance(years, list) or len(years) > 2:
        raise ExamException('Deve essere fornita una lista di due anni!')
    
    for year in years:
        if not isinstance(year, int):
           raise ExamException('Il formato degli anni deve essere un intero!') 
    
    if years[0] != years[1]-1:
        raise ExamException('Devono essere forniti due anni consecutivi!')
    
    # Si controlla la validità della list:
    if not isinstance(time_series, list): # deve essere una lista
        raise ExamException('Deve essere fornita una lista di date!') 
    
    for line in time_series:
        if not isinstance(line, list) or len(line) != 2 or not isinstance(line[0], str) or not isinstance(line[1], int):
            raise ExamException('Il formato delle date ed i valori forniti non sono validi!')
    
    #2. Si organizzano i dati in modo tale da poter trovare velocemente anno -> mese -> passeggeri
    # per tale scopo, si usa un dizionario:
    
    yearly_data = {}
    
    # Le date vengono divise tra anno e mese:
    for line in time_series:
        year = int(line[0].split('-')[0])
        month = int(line[0].split('-')[1])
        
        if year in years:
            
            # Se l'anno non è ancora presente nel dizionario si inizializza con None (e poi si andrà a popolare)
            if year not in yearly_data:
                yearly_data[year] = [None] * 12
                
            # Si converte il mese in un indice della lista (perché nella lista ci sono 11 elementi come le coppie di mesi) 
            yearly_data[year][month-1] = line[1]
    
    for year in years:
        if year not in yearly_data:
            raise ExamException(f"L'anno richiesto, {year}, non ha dati!")

    # print(yearly_data)
    
    variations = []
    for i in range(11): # si controlla Gen-Feb, Feb-Mar... etc
        var1 = None
        var2 = None
        
        if yearly_data[years[0]][i+1] is not None and yearly_data[years[0]][i] is not None:
            # print(yearly_data[years[0]][i+1])
            # print(yearly_data[years[0]][i])

            var1 = yearly_data[years[0]][i+1] - yearly_data[years[0]][i]
            
            # print(f"Differenza tra mese {i} e mese {i+1} è di {var1} nell'anno {years[0]}")
            
        if yearly_data[years[1]][i+1] is not None and yearly_data[years[1]][i] is not None:
            var2 = yearly_data[years[1]][i+1] - yearly_data[years[1]][i]   
            
            # print(f"Differenza tra mese {i} e mese {i+1} è di {var2} nell'anno {years[1]}")
            
        if var1 is None or var2 is None:
            variations.append(False)
        
        else:
            variations.append(abs(var1-var2) <= 2000) 

    return variations
        
        
# time_series_file = CSVTimeSeriesFile(name='data.csv')
# time_series = time_series_file.get_data()
# print(time_series)  
# print("\n\n")
# years = [1951, 1952]
# print(detect_similar_monthly_variations(time_series_file.get_data(), years))

