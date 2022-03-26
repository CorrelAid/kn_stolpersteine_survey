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
6. Open up [0.0.0.0:8000](0.0.0.0:8080) in your web browser

# How is the data saved?

There are three pieces of information used to uniquely identify victims: first name, last name and url.
The rest of the data is saved in the 'data' field.

Example (null, True/False might be slightly inaccurate, will have to check):

   - Vorname: Jane
   - Nachname: Doe
   - URL: doe_family.html
   - Data:
       * Gender: Frau
       * Geburtsname: Brown
       * Doktortitel: false
       * Anderenamen: null
       * Adresse: Example Street 2
       * Opfergruppen: ["juedisch", "politisch"] 
       * Familie
           * 0
              * Familienmitglied: Doe, John
              * Verwandschaftsbeziehung: Mann
       * Geburtsjahr: 1910
       * Geburtsmonat: 8
       * Geburtsdatum: null
       * Geburtsdatum_vermutet: false
       * Geburtsort: Ulm
       * Geburtsort_vermutet: false
       * Todesjahr: 1942
       * Todesmonat: 2
       * Todesdatum: null
       * Todedatum_vermutet: true
       * Todesort: KZ Example 2
       * Todesort_vermutet: false
       * Tod_in_haft: true
       * Stationen
            * 0
                * Ort: KZ Example 1
                * Stationen_af_jahr: 
                * Stationen_af_monat: 
                * Stationen_af_datum: 
                * Stationen_ed_jahr: 1941
                * Stationen_ed_monat: 
                * Stationen_ed_datum: 
            * 1
                * Ort: KZ Example 2
                * Stationen_af_jahr: 1941
                * Stationen_af_monat: 
                * Stationen_af_datum: 
                * Stationen_ed_jahr: 
                * Stationen_ed_monat: 
                * Stationen_ed_datum: 
       * Ueberlebt: nein
       
       
   
