from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        risultati = []
        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            # Filtra i consumi del mese
            consumi_mese = []
            for c in consumi:
                if c.data.month == mese:
                    consumi_mese.append(c.kwh)
            if len(consumi_mese) == 0:
                media = 0
            else:
                media = sum(consumi_mese) / len(consumi_mese)
            risultati.append((impianto.nome, media))
        return risultati




    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione"""
        """Ricerca ricorsiva della sequenza ottima di interventi nei primi 7 giorni.
        :param sequenza_parziale: lista con la sequenza scelta finora (lista di id_impianto)
        :param giorno: giorno corrente (1..7)
        :param ultimo_impianto: id dell'impianto usato il giorno precedente
        :param costo_corrente: costo accumulato fino ad ora
        :param consumi_settimana: dizionario {id_impianto: [kwh_g1, ..., kwh_g7]}"""
    # A — CONDIZIONE DI TERMINAZIONE
        if giorno > 7:
            # Se non abbiamo ancora trovato una sequenza ottima, oppure questa è migliore:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)  # copia
            return
    # Ottengo la lista degli impianti (A e B)
        for impianto_id in consumi_settimana.keys():

        # B — COSTO DELLA SCELTA DI QUESTO IMPIANTO PER QUESTO GIORNO
            costo_scelta = consumi_settimana[impianto_id][giorno - 1]

        # Aggiungo il costo di spostamento se cambio impianto
            if ultimo_impianto is not None and impianto_id != ultimo_impianto:
                costo_scelta += 5  # costo spostamento
            nuovo_costo = costo_corrente + costo_scelta

        # C — FILTRO:(evita rami peggiori)
            if self.__costo_ottimo != -1 and nuovo_costo >= self.__costo_ottimo:
                continue  # inutile proseguire su un ramo già più costoso

        # Aggiungo la scelta alla sequenza parziale
            sequenza_parziale.append(impianto_id)

        # Ricorro al giorno successivo
            self.__ricorsione(sequenza_parziale, giorno + 1, impianto_id, nuovo_costo, consumi_settimana)

        #D — BACKTRACKING
            sequenza_parziale.pop()


    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """

        diz_impianti_settimana={}
        for impianto in self._impianti:
            lista_consumi= [0]*7
            consumi=impianto.get_consumi()
            for c in consumi:
                if c.data.month == mese and 1 <= c.data.day <= 7:
                    index = c.data.day - 1
                    lista_consumi[index] = c.kwh

            diz_impianti_settimana[impianto.id] = lista_consumi

        return diz_impianti_settimana
