class SurveyObject:
    def __init__(self, questions, data, all_victims_in_database, name_append=None):
        self.possible_years = list(range(1800, 2023))
        self.possible_months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September",
                                "Oktober", "November", "Dezember"]
        self.possible_dates = list(range(1, 32))

        self.possible_family_members = ["Elternteil", "Kind", "EhegattIn", "Geschwister", "Großelternteil", "EnkelIn",
                                        "Onkel/Tante", "Cousin/Cousine", "NeffIn", "Verlobte/r", "Schwiegerelternteil",
                                        "Schwiegerkind", "SchwägerIn"]

        self.all_victim_names = []
        self.all_victim_ids = []
        for victim in all_victims_in_database:
            self.all_victim_names.append(f"{victim['Nachname']}, {victim['Vorname']}")
            self.all_victim_ids.append(victim['_id'])

        self.questions = questions
        self.data = data

        # for admin mode when we show multiple previous inputs
        if name_append is None:
            self.name_append = ""
        else:
            self.name_append = name_append


    def construct_survey(self, questions, data):
        survey = ""

        for question in questions:
            if question["type"] == "text":
                survey += self.construct_text_question(**question, data = data[question["name"]] if question["name"] in data else None)
            elif question["type"] == "checkbox":
                survey += self.construct_checkbox(**question, data = "true" if (question["name"] in data) and (data[question["name"]] == "true") else None )
            elif question["type"] == "nested-questions":
                survey += self.construct_nested_questions(**question, data=data)
            elif question["type"] == "dropdown":
                survey += self.construct_dropdown(**question, data=data)
            elif question["type"] == "dropdown_victims":
                survey += self.construct_dropdown_victims(**question, data=data)
            elif question["type"] == "date":
                survey += self.construct_date(**question, data=data)
            elif question["type"] == "form-check":
                survey += self.construct_form_check(**question, data = data[question["name"]] if question["name"] in data else None)
            elif question["type"] == "nested-dynamic":
                survey +=  self.construct_dynamic_nested(question, data)
            else:
                raise ValueError(f"{question['type']}")
            survey += f"<br>\n"

        return survey

    def construct_dynamic_nested(self, question, data):
        group_start = f"<div class='form-group' id='{question['label']}{self.name_append}'>\n" \
                      f"<label>{question['label']}:</label>"

        if question["tooltip"]:
            group_start +=  self.construct_tooltip(**question["tooltip"])

        individual_start = f"<div class='form-group-member'>\n" \
                    f"<div style='display: flex; justify-content: space-around'>\n"

        individual_end = f"</div>\n" \
                  f"<div>\n" \
                  f"<button type='button' id='delete_{question['label']}{self.name_append}' class='btn btn-primary btn-right'>löschen</button> \n" \
                  f"</div>\n" \
                  f"</div>\n" \
                  f"<br\n>" \


        group_end = f"<button type='button' id='add_{question['label']}{self.name_append}' class='btn btn-primary'>weitere {question['label']}</button>\n" \
                    f"</div>\n"

        data_fields = []
        for subquestion in question["subquestions"]:
            if subquestion["type"] != "date":
                data_fields.append(subquestion["name"])
            else:
                data_fields.extend([f"{subquestion['name']}_{time_field}" for time_field in ["jahr", "monat", "datum"]])

        if all(data_field not in data for data_field in data_fields) or all(data[data_field]=="" for data_field in data_fields):
            return group_start + individual_start + \
                   self.construct_nested_questions(**{key: val for key, val in question.items() if key not in ["tooltip", "type", "label"]},
                                                      type="nested-questions") \
                   + individual_end + group_end
        # handle all entries lists
        elif len({len(data[data_field]) for data_field in data_fields}) == 1 and all([isinstance(data[data_field],list) for data_field in data_fields]):
            all_entries = group_start
            for curr_idx in range(len(data[data_fields[0]])):
                curr_data = {data_field: (data[data_field][curr_idx]) for data_field in data_fields}
                all_entries += individual_start + self.construct_nested_questions(
                    **{key: val for key, val in question.items() if key not in ["tooltip", "type", "label"]}, type="nested-questions",
                    data=curr_data) + individual_end
            return all_entries + group_end
        # handle if only one entry -> all fields stirngs
        elif all([not isinstance(data[data_field],list) for data_field in data_fields]):
            entry = self.construct_nested_questions(
                    **{key: val for key, val in question.items() if key not in ["tooltip", "type", "label"]}, type="nested-questions",
                    data=data)
            return group_start + individual_start + entry + individual_end + group_end
        else:
            raise ValueError("Mismatch of lengths / existence of previous data!")

    def construct_tooltip(self, text, icon):
        return f"<span class='material-icons' data-toggle='tooltip' title='{text}'>{icon}</span>\n"

    def construct_text_question(self, type, name, label=None, vermutet=False, parsley_validator=None, data=None, tooltip=None):
        if type != "text":
            raise ValueError("Question must be of type 'text'")

        if data is None:
            data = {}

        if vermutet == True:
            checkbox_text = self.construct_checkbox("checkbox", f"{name}_vermutet", label="nur vermutet", data=data[f"{name}_vermutet"] if f"{name}_vermutet" in data else None)
        else:
            checkbox_text = ""

        if tooltip is not None:
            tooltip_text = self.construct_tooltip(**tooltip)
        else:
            tooltip_text = ""

        return f"<label for={name}{self.name_append}>{label if label else name}:</label>\n" \
               f"</label>\n" \
               f"<input type='text' name={name}{self.name_append} {parsley_validator if parsley_validator else ''} value={data if data else ''}>\n" \
               + tooltip_text + checkbox_text

    def construct_nested_questions(self, type, style=None, label=None, subquestions=None, data=None, tooltip=None):
        if type != "nested-questions":
            raise ValueError("Question must be of type 'nested-questions'")

        style_text = f"style={style}" if style is not None else ""
        label_text = f"<label>{label}</label>\n" if label is not None else ""

        if data is None:
            data = {}

        if tooltip is not None:
            tooltip_text = self.construct_tooltip(**tooltip)
        else:
            tooltip_text = ""

        return f"<div class='form-group' {style_text}>\n" \
               f"{label_text}\n<br>\n" \
               + self.construct_survey(subquestions, data) + tooltip_text + "\n</div>\n"

    def construct_checkbox(self, type, name, label=None, parsley_validator=None, data=None):
        if type != "checkbox":
            raise ValueError("Question must be of type 'checkbox'")

        if parsley_validator is not None:
            raise ValueError("No parsley validator is supported for checkbox type!")

        return f"<input type='checkbox' value='true' name={name}{self.name_append} {'checked' if data=='true' else ''}>\n" \
               f"<label for={name}{self.name_append}>{label if label else name}</label>\n"

    def construct_form_check(self, type, name, label, options, labels, data=None):
        if type != "form-check":
            raise ValueError("Question must be of type 'form-check'")

        if data is None:
            data = []

        option_text = ""
        for curr_option, curr_label in zip(options, labels):
            option_text += f"<div class='form-check'>\n" \
            f"<input class='form-check-input' type='checkbox' value={curr_option}, {name}{self.name_append}  {'checked' if curr_option in data else ''}>\n" \
            f"<label class='form-check-label' for={curr_option}>{curr_label}</label>\n" \
            f"</div>" \

        return f"<div class='form-group'>\n" \
               f"<label>{label}:</label>\n" \
               + option_text + "</div>\n"

    def construct_options(self, name, option_list, label_list=None, data=None):
        if data is None:
            data = {}

        if label_list is None:
            label_list=option_list

        if self.name_append == "":
            pass
        return f"<option value=''>--</option>\n" \
               + '\n'.join([f"<option selected='selected' value={curr_option}>{curr_label}</option>" \
                                if name in data and data[name] == str(curr_option) else \
                                f"<option value={curr_option}>{curr_label}</option>" \
                            for curr_option, curr_label in zip(option_list,label_list)]) + "\n"

    def construct_dropdown(self, type, name, options, label=None, label_list=None, data=None):
        if "dropdown" not in type:
            raise ValueError("Question must be of type 'dropdown'")

        return f"<div class='dropdown'>\n" \
               f"<label for={name}{self.name_append}>{label if label else name}:</label>\n" \
               f"<select name={name}{self.name_append}>\n" \
               + self.construct_options(name, options, label_list=label_list, data=data) + "</select></div>\n"

    def construct_dropdown_victims(self, type, name, data=None):
        if type != "dropdown_victims":
            raise ValueError("Question must be of type 'dropdown_victims'")

        return self.construct_dropdown(type, name, self.all_victim_ids, label_list=self.all_victim_names, data=data)

    def construct_date(self, type, name, label=None, vermutet=False, parsley_validator=None, data=None):
        if type != "date":
            raise ValueError("Question must be of type 'date'")

        if parsley_validator is not None:
            raise ValueError("No parsley validator is supported for date type!")

        if vermutet == True:
            checkbox_text = self.construct_checkbox("checkbox", f"{name}_vermutet", label="nur vermutet", data=data[f"{name}_vermutet"] if f"{name}_vermutet" in data else None)
        else:
            checkbox_text = ""

        return f"<label>{label if label else name}</label>\n" \
               f"<div class='form_date'>\n" \
               f"<select class='jahr' name='{name}_jahr{self.name_append}'>\n" \
               + self.construct_options(f"{name}_jahr", self.possible_years, data=data) + \
               f"</select>\n" \
               f"<select class='monat' name='{name}_monat{self.name_append}'>\n" \
               + self.construct_options(f"{name}_monat", self.possible_months, data=data) + \
               f"</select>\n" \
               f"<select class='datum' name='{name}_datum{self.name_append}'>\n" \
               + self.construct_options(f"{name}_datum", self.possible_dates, data=data) + \
               f"</select>\n </div> \n" + checkbox_text

