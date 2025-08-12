from numbers import Number
from typing import Tuple
from decimal import Decimal, ROUND_HALF_UP

class TupleOperations:
    @staticmethod
    def round_tuple(t : Tuple[Decimal, ...], rounding_mode = ROUND_HALF_UP) -> Tuple[Decimal, ...]:
        """Zakorągla każdy element krotki do najbliższej liczby całkowitej.

        :param t: Krotka z elementami do zaokrąglenia.
        :type t: Tuple[Decimal, ...]
        :return: Krotka z zaokrąglonymi elementami.
        :rtype: Tuple[Decimal, ...]
        """
        return tuple(elem.to_integral_value(rounding_mode) for elem in t)

    @staticmethod
    def subtract_tuples(t1 : Tuple[Decimal, ...], t2 : Tuple[Decimal, ...]) -> Tuple[Decimal, ...]:
        """Odejmowanie dwóch krotek element po elemencie.

        :param t1: Pierwsza krotka.
        :type t1: Tuple[Decimal, ...]
        :param t2: Druga krotka.
        :type t2: Tuple[Decimal, ...]
        :return: Krotka z różnicą elementów.
        :rtype: Tuple[Decimal, ...]
        """
        return tuple(a - b for a, b in zip(t1, t2))
    
    @staticmethod
    def add_tuples(t1 : Tuple[Decimal, ...], t2 : Tuple[Decimal, ...]) -> Tuple[Decimal, ...]:
        """Dodawanie dwóch krotek element po elemencie.

        :param t1: Pierwsza krotka.
        :type t1: Tuple[Decimal, ...]
        :param t2: Druga krotka.
        :type t2: Tuple[Decimal, ...]
        :return: Krotka z sumą elementów.
        :rtype: Tuple[Decimal, ...]
        """
        return tuple(a + b for a, b in zip(t1, t2))
    
    @staticmethod
    def multiply_by_scalar(t1 : Tuple[Decimal, ...], scalar: Decimal) -> Tuple[Decimal, ...]:
        """Mnoży każdy element krotki przez skalar.

        :param t1: Krotka z elementami do pomnożenia.
        :type t1: Tuple[Decimal, ...]
        :param scalar: Skalar, przez który mnożymy.
        :type scalar: Decimal
        :return: Krotka z pomnożonymi elementami.
        :rtype: Tuple[Decimal, ...]
        """
        return tuple(elem * scalar for elem in t1)
    
    @staticmethod
    def divide_by_scalar(t1 : Tuple[Decimal, ...], scalar: Decimal) -> Tuple[Decimal, ...]:
        """Dzieli każdy element krotki przez skalar.

        :param t1: Krotka z elementami do podzielenia.
        :type t1: Tuple[Decimal, ...]
        :param scalar: Skalar, przez który dzielimy.
        :type scalar: Decimal
        :return: Krotka z podzielonymi elementami.
        :rtype: Tuple[Decimal, ...]
        """
        return tuple(elem / scalar for elem in t1)
    
    @staticmethod
    def to_decimal(t : Tuple[Number, ...]) -> Tuple[Decimal, ...]:
        """Konwertuje elementy krotki do typu Decimal.

        :param t: Krotka z elementami do konwersji.
        :type t: Tuple[Number, ...]
        :return: Krotka z elementami typu Decimal.
        :rtype: Tuple[Decimal, ...]
        """
        return tuple(Decimal(elem) for elem in t)
    
    @staticmethod
    def to_int(t : Tuple[Decimal, ...]) -> Tuple[int, ...]:
        """Konwertuje elementy krotki do typu int.

        :param t: Krotka z elementami do konwersji.
        :type t: Tuple[Decimal, ...]
        :return: Krotka z elementami typu int.
        :rtype: Tuple[int, ...]
        """
        return tuple(int(elem) for elem in t)