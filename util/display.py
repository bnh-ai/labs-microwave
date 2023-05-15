################################################################################
# This software is being provided under the Creative Commons                   #
# Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)  #
# license. For more information about the restrictions associated with this    #
# license, see                                                                 #
#                                                                              #
#   https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode                #
#                                                                              #
# The information provided by this notebook does not contain specific legal    #
# advice and use of this information does not create an attorney-client        #
# relationship with BNH.AI.                                                    #
################################################################################

import os
from sys import getsizeof
from io import BytesIO
import time

import pandas as pd
from pandas.api.types import is_numeric_dtype

from IPython.display import display, HTML, Javascript

from ipywidgets import HTML as Html
from ipywidgets import Button, Checkbox, FileUpload, Label, Layout, Output, RadioButtons, HBox, GridspecLayout
from ipywidgets import __version__ as ipywidgets_version

from util.bias_testing import BiasTester
from util.exceptions import html_error_message

VERSION = 'Microwave-1.23.1-20230515-rc8'
COLAB = 'google.colab' in str(get_ipython())
GITHUB = "labs-microwave"

class JupyterFormManager(object):

    def __init__(self):

        self.verbose = False

        if COLAB:
            def resize_colab_cell():
                display(Javascript('google.colab.output.setIframeHeight(0, true, {maxHeight: 5000})'))
            get_ipython().events.register('pre_run_cell', resize_colab_cell)
        else:
            javascript_string = """
                IPython.OutputArea.prototype._should_scroll = function(lines) {
                    return false;
                }
                IPython.notebook.set_autosave_interval(0);
            """
            display(Javascript(javascript_string))

        self.popup_message = """
            require(
                ["base/js/dialog"], 
                function(dialog) {
                    dialog.modal({
                        title: '$title',
                        body: '$body',
                        buttons: {
                            'OK': {}}
                    });
                }
            );
        """

        self.html_label = """
            <div style="height:50px; font-weight:bold"> 
                <p>%s</p>
            </div> 
        """
        self.html_label_tall = """
            <div style="height:100px; font-weight:bold"> 
                <p>%s</p>
            </div> 
        """

        self.widgets = {}

        self.widgets['sample_data_context'] = Output()
        self.widgets['file_upload_context'] = Output()
        self.widgets['file_upload_message_context'] = Output()
        self.widgets['select_model_output_context'] = Output()
        self.widgets['select_demographic_categories_context'] = Output()
        self.widgets['run_test_button_context'] = Output()
        self.widgets['message_context'] = Output()
        self.widgets['test_output_context'] = Output()

        if COLAB:
            display(HTML("<p><i>Notebook initialized. Now that it is initialized, running the next cell will allow you to perform bias testing using a sample dataset.</i></p>"))

    def start(self):

        margin_left = "0px" if COLAB else "51px"

        html_string = f"""

            <style>
                .blue_button {{
                  background-color: #004F9D; 
                  border: none;
                  margin-top: 30px;
                  margin-left: 30px;
                  color: white;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 16px;
                  height : 50px;
                  line-height : 50px;
                  width : 250px
                }}
                .bold_label {{
                  font-size : 14px; 
                  font-weight : bold;
                  margin-left : {margin_left};
                }}
                #T_nyc_air_category_test {{margin-left: auto; margin-right: auto;}}
                #T_nyc_air_intersectional_test {{margin-left: auto; margin-right: auto;}}
            </style>

            <br> 

        """

        if COLAB:

            html_string += f"""
            <p>
                Please click on one of the buttons below to select a dataset for analysis.
            </p>

            <br> 

            <p>
                You may provide your own sample data or use a synthetic 
                <a href="javascript:void(0);" onclick="window.open('https://github.com/bnh-ai/{GITHUB}/tree/main/data','_blank');">sample dataset</a> 
                provided by <a href="javascript:void(0);" onclick="window.open('https://bnh.ai','_blank');">BNH.AI</a> for testing purposes.  
                To use your own sample data, click on the "Upload" button below.  To use a synthetic sample dataset provided by 
                <a href="javascript:void(0);" onclick="window.open('https://bnh.ai','_blank');">BNH.AI</a> for testing purposes, 
                click on either the "Use Sample Selection Data" or "Use Sample Scoring Data" button.
            </p>

            <br> 

            """
        else:

            html_string += """
            <p>
                Please click on the "Upload" button below to upload a dataset for analysis.
            </p>

            <br> 

            <p>
                You may provide your own sample data or use a synthetic sample dataset located in the <tt>data</tt> folder included in this distribution 
                which has been provided by <a href="javascript:void(0);" onclick="window.open('https://bnh.ai','_blank');">BNH.AI</a> for testing purposes.
            </p>

            <br> 

            """

        html_string += """
            <p>
                Note that the law requires testing across the categories of race/ethnicity and sex category, 
                as well as intersectional categories for both.  If you upload a dataset of your own, 
                it must meet the following criteria: 
            </p>

            <p>
                <ul>
                    <li>The dataset must be in the form of a CSV file.
                    <li>The variable which contains the model output must either be a binary variable containing the value 0 or 1 (reflecting a binary classification model used for the selection of employees or candidates) or be continuously valued (reflecting a regression model used for scoring employees or candidates).
                    <ul>
                        <li>A variable encoding selection should use the value 1 to reflect selection (and 0 otherwise). 
                        <li>Increasing values of a variable encoding scoring are assumed to reflect more favorable results. 
                    </ul>
                    <li>The dataset must contain at least 100, but no more than 10,000, observations and be no greater than 10 MB in size.
                    <li>There must be at least two binary demographic variables that are indicators of race/ethnicity which encode demographic category membership with a value of 1 reflecting category membership (and 0 otherwise).
                    <li>The same applies for demographic variables that are indicators of sex category.
                    <li>There may be no null values in the model output or demographic variables.
                </ul>
            </p>

            <br> 

            """

        display(Html(html_string))

        display(self.widgets['sample_data_context'])
        display(self.widgets['file_upload_context'])
        display(self.widgets['file_upload_message_context'])
        display(self.widgets['select_model_output_context'])
        display(self.widgets['select_demographic_categories_context'])
        display(self.widgets['run_test_button_context'])
        display(self.widgets['test_output_context'])
        display(self.widgets['message_context'])

        if COLAB:

            self.widgets['sample_selection_data_widget'] = Button(description='Use Sample Selection Data')
            self.widgets['sample_selection_data_widget'].add_class("blue_button")
            self.widgets['sample_selection_data_widget'].on_click(self.get_dataset)

            self.widgets['sample_scoring_data_widget'] = Button(description='Use Sample Scoring Data')
            self.widgets['sample_scoring_data_widget'].add_class("blue_button")
            self.widgets['sample_scoring_data_widget'].on_click(self.get_dataset)

            self.widgets['file_upload_widget'] = FileUpload(accept='.csv', multiple=False)
            self.widgets['file_upload_widget'].add_class("blue_button")
            self.widgets['file_upload_widget'].observe(self.get_dataset, 'value')

            self.widgets['file_upload_hbox_widget'] = HBox([self.widgets['file_upload_widget'], self.widgets['sample_selection_data_widget'], self.widgets['sample_scoring_data_widget']])

            with self.widgets['file_upload_context']:
                display(self.widgets['file_upload_hbox_widget'])

        else:

            self.widgets['file_upload_widget'] = FileUpload(accept='.csv', multiple=False)
            self.widgets['file_upload_widget'].add_class("blue_button")
            self.widgets['file_upload_widget'].observe(self.get_dataset, 'value')

            with self.widgets['file_upload_context']:
                display(self.widgets['file_upload_widget'])

    def get_dataset(self, file_widget_data):

        try:

            self.widgets['file_upload_message_context'].clear_output()
            self.widgets['message_context'].clear_output()
            tic = time.perf_counter()
            if isinstance(file_widget_data, Button):
                description = file_widget_data.description
                if description == "Use Sample Selection Data":
                    filename = "sample_candidate_selection_data.csv"
                elif description == "Use Sample Scoring Data":
                    filename = "sample_candidate_scoring_data.csv"
                else:
                    raise Exception(f"Button description {description} not recognized")
                if COLAB:
                    self.dataset_filename = f".{os.sep}{GITHUB}{os.sep}data{os.sep}{filename}"
                else:
                    self.dataset_filename = f"..{os.sep}data{os.sep}{filename}"
                with self.widgets['file_upload_message_context']:
                    display(HTML("<br><br>"))
                    display(HTML(f"<p><i>Parsing contents of file '{filename}'</i></p>"))
                try:
                    self.dataset = pd.read_csv(self.dataset_filename)
                except Exception as e:
                    raise Exception(f"The Python Pandas CSV file parser was unable to read the file {self.dataset_filename} and returned the following error message: {e}")
                toc = time.perf_counter()
                with self.widgets['file_upload_message_context']:
                    display(HTML(f"<p>&nbsp;&nbsp;&nbsp;<i>Dataset containing {self.dataset.shape[0]} observations parsed in {toc - tic:0.4f} seconds.</i></p>"))
                    display(HTML("<br>"))
            elif isinstance(file_widget_data['new'], dict):
                # Applies when ipywidgets<=7.7.2
                files = list(file_widget_data['new'].keys())
                self.dataset_filename = file_widget_data['new'][files[0]]['metadata']['name']
                with self.widgets['file_upload_message_context']:
                    display(HTML("<br><br>"))
                    display(HTML(f"<p><i>Parsing contents of file '{self.dataset_filename}'</i></p>"))
                if getsizeof(file_widget_data['new'][files[0]]['content']) > 1024*1024*10:
                    raise Exception(f"The file size is limited to 10MB but file '{self.dataset_filename}' contains {getsizeof(file_widget_data['new'][files[0]]['content'])} bytes")
                try:
                    self.dataset = pd.read_csv(BytesIO(file_widget_data['new'][files[0]]['content']))
                except Exception as e:
                    raise Exception(f"The Python Pandas CSV file parser was unable to read the file and returned the following error message: {e}")
                toc = time.perf_counter()
                with self.widgets['file_upload_message_context']:
                    display(HTML(f"<p>&nbsp;&nbsp;&nbsp;<i>Dataset containing {self.dataset.shape[0]} observations parsed in {toc - tic:0.4f} seconds.</i></p>"))
                    display(HTML("<br>"))
            elif isinstance(file_widget_data['new'], tuple):
                # Applies when ipywidgets>7.7.2
                files = list(file_widget_data['new'])
                self.dataset_filename = files[0]['name']
                with self.widgets['file_upload_message_context']:
                    display(HTML("<br><br>"))
                    display(HTML(f"<p><i>Parsing contents of file '{self.dataset_filename}'</i></p>"))
                if getsizeof(files[0]['content']) > 1024*1024*10:
                    raise Exception(f"The file size is limited to 10MB but the file '{self.dataset_filename}' contained contains {getsizeof(files[0]['content'])} bytes")
                try:
                    self.dataset = pd.read_csv(BytesIO(files[0]['content']))
                except Exception as e:
                    raise Exception(f"The Python Pandas CSV file parser was unable to read the file and returned the following error message: {e}")
                toc = time.perf_counter()
                with self.widgets['file_upload_message_context']:
                    display(HTML(f"<p>&nbsp;&nbsp;&nbsp;<i>Dataset containing {self.dataset.shape[0]} observations parsed in {toc - tic:0.4f} seconds.</i></p>"))
                    display(HTML("<br>"))
            else:
                raise Exception(f"Value returned by FileUpload widget has unexpected type [{type(file_widget_data['new'])}]")
            if self.dataset.shape[0] < 100:
                raise Exception(f"The file {self.dataset_filename} has only {self.dataset.shape[0]} observations, but should have a minimum of 100 observations")
            if self.dataset.shape[0] > 10000:
                raise Exception(f"The test dataset is limited to 10,000 observations, but the file {self.dataset_filename} has {self.dataset.shape[0]} observations")
            self.display_dataset_widgets()
            if COLAB:
                self.widgets['sample_selection_data_widget'].disabled = True
                self.widgets['sample_scoring_data_widget'].disabled = True
            self.widgets['file_upload_widget'].disabled = True

        except Exception as e:

            self.widgets['file_upload_message_context'].clear_output()
            with self.widgets['message_context']:
                display(HTML(html_error_message(exception=e, stack_trace=self.verbose, context=f"Unable to retrieve data from file '{self.dataset_filename}'")))

    def validate_input(self): 

        self.columns = self.dataset.columns.values.tolist()

        self.model_output_label = self.widgets['select_model_output_radiobutton'].value

        n_rows = self.widgets['select_demographic_categories_grid'].n_rows
        self.race_labels = [
            self.widgets['select_demographic_categories_grid'][i, 0].value for i in range(1, n_rows)
                if self.widgets['select_demographic_categories_grid'][i, 1].value == True
        ]
        self.gender_labels = [
            self.widgets['select_demographic_categories_grid'][i, 0].value for i in range(1, n_rows)
                if self.widgets['select_demographic_categories_grid'][i, 2].value == True
        ]

        if self.model_output_label is None:
            raise Exception("No selection was made for the variable used to store the model output")
        if not is_numeric_dtype(self.dataset[self.model_output_label]):
            raise Exception(f"The variable '{self.model_output_label}' used to store the model output should be a numeric variable but is of type '{self.dataset.dtypes[self.model_output_label]}'")

        model_output_nulls = self.dataset[self.dataset[self.model_output_label].isna()].shape[0]
        if model_output_nulls > 0:
            raise Exception(f"The dataset should not contain nulls, but there appear to be {model_output_nulls} null values for '{self.model_output_label}'")

        unique_values = sorted(self.dataset[self.model_output_label].unique())
        if len(unique_values) < 2:
            raise Exception(f"There were only {len(unique_values)} values found for the '{self.model_output_label}' variable")
        elif len(unique_values) == 2:
            if unique_values[0] != 0 or unique_values[1] != 1:
                raise Exception(f"The values of the '{self.model_output_label}' variable appear to be binary, but take on values {unique_values[0]} and {unique_values[1]} (rather than 0 and 1)")
            self.output_type = "binary"
        else:
            self.output_type = "continuous"

        if self.output_type == "continuous":
            minimum = self.dataset[self.model_output_label].min()
            maximum = self.dataset[self.model_output_label].max()
            if maximum - minimum < 1e-4:
                raise Exception(f"The values of the '{self.model_output_label}' variable appear to be continuous, but the maximum and minimum values ({maximum} and {minimum}) are effectively the same")

        if self.model_output_label in self.race_labels:
            raise Exception(f"The variable '{self.model_output_label}' used to store the model output cannot be also be a race indicator")
        if self.model_output_label in self.gender_labels:
            raise Exception(f"The variable '{self.model_output_label}' used to store the model output cannot be also be a sex indicator")

        if len(self.race_labels) < 2:
            raise Exception("At least two variables corresponding to race must be identified")
        if len(self.gender_labels) < 2:
            raise Exception("At least two variables corresponding to sex must be identified")
        for label in self.race_labels + self.gender_labels:
            unique_values = sorted(self.dataset[label].unique())
            if len(unique_values) == 2:
                if unique_values[0] != 0 or unique_values[1] != 1:
                    raise Exception(f"The values of the '{label}' variable appear to be binary, but take on values {unique_values[0]} and {unique_values[1]} (rather than 0 and 1)")
            else:
                raise Exception(f"The values of the demographic variable '{label}' should be a binary variable with values of 0 and 1 indicating category membership, but contains {len(unique_values)} unique values")
        for label in self.race_labels:
            if label in self.gender_labels:
                raise Exception(f"The indicator '{label}' cannot be both a race and sex indicator")
        for label in self.gender_labels:
            if label in self.race_labels:
                raise Exception(f"The indicator '{label}' cannot be both a race and sex indicator")

        return True

    def display_dataset_widgets(self): 

        try:

            columns = self.dataset.columns.values.tolist()

            self.widgets['select_model_output_label'] = Html(
                    self.html_label % "Please select the variable used to store the model output. If using the sample data provided, select \"Model Output\" below."
            )
            self.widgets['select_model_output_label'].add_class('bold_label')
            self.widgets['select_model_output_radiobutton'] = RadioButtons(
                    layout=Layout(margin="0px 0px 30px 81px"),
                    options=columns,
                    value=None
            )
            with self.widgets['select_model_output_context']:
                display(self.widgets['select_model_output_label'])
                display(self.widgets['select_model_output_radiobutton'])

            self.widgets['select_demographic_categories_label'] = Html(
                self.html_label_tall % "Please identify which variables encode sex category or race/ethnicity information. The variables should be binary, with 0 or 1 indicating category membership. If using the sample data provided, select \"Male\" and \"Female\" for the sex category and \"Hispanic or Latino\", \"White\", etc. for the race/ethnicity variables."
            )
            self.widgets['select_demographic_categories_label'].add_class('bold_label')
            self.widgets['select_demographic_categories_grid'] = GridspecLayout(
                len(columns) + 1, 3, layout=Layout(margin="0px 0px 30px 81px")
            )
            demographic_grid_labels = [Label('Variable Name'), Label('Race/Ethnicity'), Label('Sex Category')]
            for label in demographic_grid_labels:
                label.add_class('bold_label')
            variable_labels = [Label(c) for c in columns]
            for i in range(len(demographic_grid_labels)):
                self.widgets['select_demographic_categories_grid'][0, i] = demographic_grid_labels[i]
                if not COLAB:
                    if i == 0:
                        self.widgets['select_demographic_categories_grid'][0, i].layout.right = '20px'
                    elif i == 1:
                        self.widgets['select_demographic_categories_grid'][0, i].layout.right = '80px'
                    elif i == 2:
                        self.widgets['select_demographic_categories_grid'][0, i].layout.right = '250px'
                    else:
                        raise Exception(f"Unexpected index {i} for demographic grid labels")
            for i in range(1, len(variable_labels) + 1):
                self.widgets['select_demographic_categories_grid'][i, 0] = variable_labels[i - 1]
                if not COLAB:
                    self.widgets['select_demographic_categories_grid'][i, 0].layout.width = '200px'
                for j in range(1, 3):
                    self.widgets['select_demographic_categories_grid'][i, j] = Checkbox(description='', value=None, indent=False)
                    if not COLAB:
                        if j == 1: self.widgets['select_demographic_categories_grid'][i, j].layout.left = '7px'
                        if j == 2: self.widgets['select_demographic_categories_grid'][i, j].layout.right = '160px'

            with self.widgets['select_demographic_categories_context']:
                display(self.widgets['select_demographic_categories_label'])
                display(self.widgets['select_demographic_categories_grid'])

            self.widgets['run_tests_button'] = Button(description='Run Tests')
            self.widgets['run_tests_button'].add_class('blue_button')
            self.widgets['run_tests_button'].on_click(self.nyc_air_test)        
            with self.widgets['run_test_button_context']:
                display(self.widgets['run_tests_button'])

        except Exception as e:

            self.widgets['message_context'].clear_output()
            with self.widgets['message_context']:
                display(HTML(html_error_message(exception=e, stack_trace=self.verbose, context=f"Unable to render user input Jupyter widgets based on file {self.dataset_filename}")))


    def nyc_air_test(self, button_widget):

        try:

            self.widgets['test_output_context'].clear_output()
            self.widgets['message_context'].clear_output()

            with self.widgets['test_output_context']:
                display(HTML("<br><br>"))
                display(HTML("<p><i>Checking the inputs ...</i></p>"))

            self.validate_input()

            with self.widgets['test_output_context']:
                display(HTML(f"<p><i>&nbsp;&nbsp;&nbsp;The inputs look good. Based on the values of the '{self.model_output_label}' variable, it appears that the model produces {self.output_type} output.</i></p>"))
                display(HTML("<br>"))

            tic = time.perf_counter()
            with self.widgets['test_output_context']:
                display(HTML("<p><i>Calculating AIR test results ...</i></p>"))

            tester = BiasTester(
                dataset=self.dataset,
                model_output_label=self.model_output_label,
                race_labels=self.race_labels,
                gender_labels=self.gender_labels,
                output_type=self.output_type
            )
            category_results = tester.nyc_air_test(categorization="category")
            intersectional_results = tester.nyc_air_test(categorization="intersectional")
            toc = time.perf_counter()
            with self.widgets['test_output_context']:
                display(HTML(f"<p>&nbsp;&nbsp;&nbsp;<i>Test results calculated in {toc - tic:0.4f} seconds.</i></p>"))

            category_style = tester.format_results_table(results_table=category_results, categorization="category").style
            intersectional_style = tester.format_results_table(results_table=intersectional_results, categorization="intersectional").style
            
            for style in [category_style, intersectional_style]:
                style.set_table_styles( [ { 'selector': 'th', 'props': [('text-align', 'center')] } ] )
                style.format(formatter=None, precision=2, na_rep='<a href="javascript:void(0);" onclick="alert(\'This value could not be calculated because it would have produced a divide by zero error or otherwise generated an undefined value.\'); return false;">N/A</a>')

            category_styled_output = category_style.applymap(lambda x: 'background-color: #ffffff;').hide(axis='index')
            intersectional_styled_output = intersectional_style.applymap(lambda x: 'background-color: #ffffff;').hide(axis='index')

            category_styled_output.set_uuid("nyc_air_category_test")
            intersectional_styled_output.set_uuid("nyc_air_intersectional_test")

            if self.output_type == "binary":

                nyc_air_category_test_html = """
                    <br><br>
                    <b>NYC DCWP Adverse Impact Ratio Category-Level Test</b>
                    <br><br>
                    Adverse Impact Ratio (AIR) tests attempt to measure the relative rates of positive 
                    outcomes for different demographic categories.  
                    <br><br>
                    This AIR calculation is performed for each demographic category consistently with that described in 
                    the Department of Consumer and Worker Protection April 2023 Notice of Adoption of Final Rule, based on 
                    the output of a model that selects employees or candidates (i.e., a binary classifier).
                    <br><br>
                    The selection rate (<b>Selection Rate</b>) in each demographic category, which reflects the number selected 
                    (<b># Selected</b>) relative to the total number in the category (<b># of Applicants</b>), is compared with the highest rate across 
                    categories in the demographic group (such as race/ethnicity or sex category).
                    <br><br>
                """

                nyc_air_intersectional_test_html = """
                    <br><br>
                    <b>NYC DCWP Adverse Impact Ratio Intersectional Category Test</b>
                    <br><br>
                    This AIR calculation is similar to the category-level AIR
                    calculation described above, but is based on intersectional
                    categories.
                    <br><br>
                """

            elif self.output_type == "continuous":

                nyc_air_category_test_html = """
                    <br><br>
                    <b>NYC DCWP Adverse Impact Ratio (AIR) Category-Level Test</b>
                    <br><br>
                    Adverse Impact Ratio (AIR) tests attempt to measure the relative rates of positive 
                    outcomes for different demographic categories. 
                    <br><br>
                    This AIR calculation is performed for each demographic
                    category consistently with the Department of Consumer and
                    Worker Protection April 2023 Notice of Adoption of Final Rule, based on the
                    output of a model that generates scores (i.e., a regression model). 
                    <br><br>
                    The scoring rate (<b>Scoring Rate</b>) in each demographic
                    category, which reflects the number with scores greater 
                    than the overall median relative to the total number in the
                    category, is compared with the highest rate across
                    categories in the demographic group (such as race/ethnicity or sex category). 
                    <br><br>
                """

                nyc_air_intersectional_test_html = """
                    <br><br>
                    <b>NYC DCWP Adverse Impact Ratio (AIR) Intersectional Category Test</b>
                    <br><br>
                    This AIR calculation is similar to the category-level AIR
                    calculation described above, but is based on intersectional
                    categories.
                    <br><br>
                """

            else:

                raise Exception(f"Model output type {self.output_type} not recognized")

            with self.widgets['test_output_context']:
                display(HTML(nyc_air_category_test_html))
                display(category_styled_output)
                display(HTML(nyc_air_intersectional_test_html))
                display(intersectional_styled_output)

            concluding_message_html = f"""
            <br>
            <p style="font-weight:bold">
                Please contact BNH.AI via <a href="mailto:luminos@bnh.ai">email</a> 
                with additional questions, and visit 
                <a href="javascript:void(0);" onclick="window.open('https://bnh.ai','_blank');">our website</a> 
                to learn more about how we perform audits to assess AI systems for risk.
            </p>
            <br>
            """

            if COLAB:
                concluding_message_html += f"""
                <p style="font-weight:bold">
                    If you would like to try again, please select "Runtime", then
                    "Run all" from the menu above.
                </p>
                <br>
                """
            else:
                concluding_message_html += f"""
                <p style="font-weight:bold">
                    If you would like to try again, please select "Kernel", then
                    "Restart & Run All" from the menu above.
                </p>
                <br>
                """

            with self.widgets['test_output_context']:
                display(HTML(concluding_message_html))

            self.widgets['run_tests_button'].disabled = True

        except Exception as e:

            self.widgets['test_output_context'].clear_output()
            self.widgets['message_context'].clear_output()
            with self.widgets['message_context']:
                display(HTML(html_error_message(exception=e, stack_trace=self.verbose, context=f"Unable to render test results based on file {self.dataset_filename}")))

