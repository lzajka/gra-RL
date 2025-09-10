

class Transaction():
    """Klasa pozwalająca na tworzenie transakcji
    """
    def __init__(self, parent):
        """Inicjuje obiekt typu Transaction

        :param parent: Obiekt na którym mają być wykonywane operacje.
        """
        self._temps = dict()
        self._managed = parent    

    def _check_key(self, key):
        if not hasattr(self._managed, key):
            raise KeyError(f'Obiekt nie posiada klucza {key}')

    def get_temp(self, key : str):
        """Zwraca wartość tymczasowego parametru.
        UWAGA: Należy się upewnić, że wykonane operacje nie zmienią wartości oryginalnego obiektu.

        :param key: Klucz parametru
        :type key: str
        :name: Nazwa grupy
        :return: Jeżeli wartość obiektu została nadpisana zwraca wartość tymczasową, w przeciwnym wypadku oryginał.
        """
        self._check_key(key)
        return self._temps.get(key, getattr(self._managed, key))
    
    def write_temp(self, key : str, value):
        """Ustawia wartość tymczasową dla danego parametru.

        :param key: Klucz parametru
        :type key: str
        :param value: Wartość parametru
        """
        self._check_key(key)
        self._temps[key] = value

    def commit(self):
        """Ustawia wartości rodzica zgodnie z wartościami tymczasowymi.
        Domyślnie przypisuje nową wartość zmiennym. 
        """

        for (key, value) in self._temps.items():
            self._check_key(key)
            setattr(self._managed, key, value)
