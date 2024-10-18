1. ~~START, zgłoszenie, zapisany czas rozpoczęcia -> wysłanie zgodnie ze zgłoszeniem jednostek -> rozponanie -> więcej jednostek -> pomaganie i transport -> wszyscy w szpitalu, KONIEC, zapisanie czasu zakończenia~~
2. dodatkowe zgłoszenia - dodatkowe scenariusze, ale małe, w różnych miejscach?
3. ~~odległości między miejscami - w pliku? Funkcje sprawdzić, współrzędne z adresów też~~
4. ~~Pacjenci - na bazie profili, wszystkie informacje jakie są w profilu + id, różne stany (wszystkie trzeba zapisać!), obliczanie RPM, tablica pogarszania się RPM - metoda ZmniejszRPM czy coś, czas przyjęcia do szpitala~~
5. ~~ZRMy - wszystkie rzeczy z tabelki, pacjenta mogą przewozić w sobie tylko jednego, lokalizacja teraz i docelowa, czy są w drodze obecnie, za ile będą u celu, zależnie od typu 2 lub 3 osoby, jakaś kolejka gdzie następnie (zastępczy cel? Nowy cel?)~~
6. ~~Szpitale - to co w tabelce? transfer pacjenta (odjęcie z karetki, dodanie na SOR!!!) -> kilka minut na sprawdzenie i potem na odpowiednim oddziele zajmuje miejsce (miejsce--)~~
7. ~~Kolejkowanie na podstawie triażu, a potem RPM - decyzje zapamiętywane zgodnie z rozwiązaniem: [(i, Pi, ZRMi, SORi, Ti)...], Ti - kiedy przyjęty do szpitala~~
8. Funkcje celu:
    - liczba zmarłych na koniec (RPM = 0) MIN
    - średni RPM pacjentów wszystkich MAX
    - czas trwania symulacji (od zgłoszenia do zakończenia) MIN
    - średni czas udzielania pomocy (dla każdego pacjenta, czas przyjęcia do szpitala - czas zgłoszenia) MIN

    Powinno się dać wybrać wagi każdej funkcji - domyślne wagi jakieś też, ale najpierw zobaczyć jakie będą wyniki wszystkich czterech
9. ~~Pacjenci wysyłani do najbliższego szpitala o zgodnej dziedzinie, musi też mieć miejsce (UWAGA - może być tak, że ktoś tam już jedzie, co wtedy? Albo zostawić i będzie trzeba nagle zmieniać jeśli szpital zajęty, albo trzebaby trzymać liczbę "zablokowanych" łóżek, dopóki pacjent nie przyjedzie)~~
10. ~~Gdy ratownicy w symulacji spotykają poszkodowanego, muszą ogarnąć stan i potem na podstawie tego jaka jest procedura zapisana do pacjenta, wykonać jeśli się da (KATEGORIA_RATOWNICZA = 15), co zajmuje czas i zmienia stan odpowiednio, jeśli to była krytyczna procedura~~
11. ~~Scenariusze - utworzenie pacjentów na podstawie liczby wg profili~~