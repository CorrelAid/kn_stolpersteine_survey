General information about the project to which this repository belongs can be found [here](https://pad.correlaid.org/zHZbVjb4TS6Vntt4XpnrBA?both).

For issues associated with the whole project take a look at [this](https://github.com/orgs/CorrelAid/projects/10)

# How do I run this locally?

You can run this locally, setting up the database the first time is the hardest part:

1. First, if you haven't already, install MongoDB: [https://docs.mongodb.com/manual/administration/install-community/](https://docs.mongodb.com/manual/administration/install-community/)
2. Start the server / MongoDB shell by running `mongod` on the command line
    > **_NOTE:_**  MongoDB actually doesn't create the database/document until an entry is inputted. So you don't have to do anything in the shell, although you could run `show dbs` later to verify the database was created.
3. Create a .env file with the local `MONGODB_URI` in it along with the PORT you want to run the survey on `8080`, e.g.:
    ```
    touch .env
    echo "MONGODB_URI=localhost:27017" > .env
    echo "PORT=8080" >> .env
    ```
4. Install the python requirements (best to do in a virtual environment):
    ```
    pip install -r requirements.txt
    ```
5. Run main.py (`python main.py` on the command line)
6. Open up [0.0.0.0:8000](0.0.0.0:8080) your web browser

# How is the data saved?

There are three pieces of information used to uniquely identify victims: first name, last name and url.
The rest of the data is saved in the 'data' field.

Example (null, True/False might be slightly inaccurate, will have to check):

   - vorname: Jane
   - nachname: Doe
   - url: doe_family.html
   - data:
       * geburtsname: Brown
       * doktortitel: false
       * anderenamen: null
       * adresse: Example Street 2
       * opfergruppen: ["juedisch", "politisch"]
       * geburtsjahr: 1910
       * familie
           * 0
              * familienmitglied: Doe, John
               * verwandtschaftsgrad: Mann
       * geburtsjahr: 1910
       * geburtsmonate: 8
       * geburtsdatum: null
       * geburtsdatum_vermutet: false
       * geburtsort: Ulm
       * geburtsort_vermutet: false
       * todesjahr: 1942
       * todesmonat: 2
       * todesdatum: null
       * todedatum_vermutet: true
       * todesort: KZ Example 2
       * todesort_vermutet: false
       * tod_in_haft: true
       * stationen
            * 0
                * haftorte: KZ Example 1
                * stationen_af_jahr: 
                * stationen_af_monat: 
                * stationen_af_datum: 
                * stationen_ed_jahr: 1941
                * stationen_ed_monat: 
                * stationen_ed_datum: 
            * 1
                * haftorte: KZ Example 2
                * haftorte: KZ Example 1
                * stationen_af_jahr: 1941
                * stationen_af_monat: 
                * stationen_af_datum: 
                * stationen_ed_jahr: 
                * stationen_ed_monat: 
                * stationen_ed_datum: 
       * ueberlebt: nein
       
       
   
