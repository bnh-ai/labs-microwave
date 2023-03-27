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

import itertools
import numpy as np
import pandas as pd

pd.set_option('mode.use_inf_as_na', True)

class BiasTester(object):

    def __init__(self,
                 dataset: pd.DataFrame = None,
                 model_output_label: str = None,
                 race_labels: list = None,
                 gender_labels: list = None,
                 output_type: str = None):
        self.dataset = dataset
        self.model_output_label = model_output_label
        self.race_labels = race_labels
        self.gender_labels = gender_labels
        self.output_type = output_type
        self.columns = dataset.columns.values.tolist()

    def nyc_air_test(self, categorization: str = None) -> pd.DataFrame:

        if self.output_type == 'binary':

            if categorization == 'category': 

                category_df = pd.DataFrame(columns=["Group", "Category", "N(Cat)", "Pos(Cat)", "P(Cat)"])
                category_ttl = {}
                category_pos = {}
                category_p = {}
                for category in self.gender_labels + self.race_labels:
                    group = "Race/Ethnicity" if category in self.race_labels else "Sex"
                    (category_ttl[category], category_pos[category], category_p[category]) = self.predicted_positive_ratio(category=category)
                    category_df = pd.concat((category_df, pd.DataFrame([{
                        "Group": group,
                        "Category": category, 
                        "N(Cat)": category_ttl[category], 
                        "Pos(Cat)": category_pos[category], 
                        "P(Cat)": category_p[category]}])), axis=0, ignore_index=True
                    )
                group_max = {}
                for group in category_df['Group'].unique():
                    group_df = category_df[category_df['Group'] == group]
                    group_max[group] = group_df['P(Cat)'].max()
                category_df['__GROUP_MAX__'] = category_df.apply(lambda row: group_max[row['Group']], axis=1)
                category_df['NYC AIR'] = category_df['P(Cat)'] / category_df['__GROUP_MAX__']
                category_df.drop(columns=['__GROUP_MAX__'], inplace=True)
                return category_df
                        
            elif categorization == 'intersectional':

                intersectional_df = pd.DataFrame(columns=["Intersectional Category", "N(Cat)", "Pos(Cat)", "P(Cat)"])
                combo_ttl = {}
                combo_pos = {}
                combo_p = {}
                set_of_categorys = [ self.gender_labels, self.race_labels ]
                for combo in itertools.product(*set_of_categorys):
                    category_list = [x for x in combo]
                    category_list.reverse()
                    intersectional_category = " ".join(category_list)
                    combo_id = "::".join(combo)
                    filters = []
                    for category in combo:
                        filter = self.dataset[category] == 1
                        filters.append(filter)
                    intersection = np.logical_and(*filters)
                    (combo_ttl[combo_id], combo_pos[combo_id], combo_p[combo_id]) = self.predicted_positive_ratio(boolean_array=intersection)
                    df_row_dict = {
                        'Intersectional Category': intersectional_category,
                        'N(Cat)': combo_ttl[combo_id],
                        'Pos(Cat)': combo_pos[combo_id],
                        'P(Cat)': combo_p[combo_id],
                    }
                    intersectional_df = pd.concat((intersectional_df, pd.DataFrame([df_row_dict])), axis=0, ignore_index=True)
                intersectional_max = intersectional_df['P(Cat)'].max()
                intersectional_df['NYC AIR'] = intersectional_df['P(Cat)'] / intersectional_max
                return intersectional_df

            else:

                raise Exception(f"Categorization [{categorization}] not recognized") 

        elif self.output_type == 'continuous':

            value_med = float(self.dataset[self.model_output_label].median())

            if categorization == 'category': 

                category_df = pd.DataFrame(columns=["Group", "Category", "N(Cat)", "MedPos(Cat)", "MedP(Cat)"])
                category_ttl = {}
                category_medpos = {}
                category_medp = {}
                for category in self.gender_labels + self.race_labels:
                    group = "Race/Ethnicity" if category in self.race_labels else "Sex"
                    category_ttl[category] = self.dataset[self.dataset[category] == 1].shape[0]
                    category_medpos[category] = self.dataset[(self.dataset[category] == 1) & (self.dataset[self.model_output_label] > value_med)].shape[0]
                    if category_ttl[category] > 0:
                        category_medp[category] = category_medpos[category] / category_ttl[category]
                    else:
                        raise Exception(f"No observations were found in the dataset for the demographic category {category}")
                    category_df = pd.concat((category_df, pd.DataFrame([{
                        "Group": group,
                        "Category": category, 
                        "N(Cat)": category_ttl[category], 
                        "MedPos(Cat)": category_medpos[category], 
                        "MedP(Cat)": category_medp[category]}])), axis=0, ignore_index=True
                    )
                group_max = {}
                for group in category_df['Group'].unique():
                    group_df = category_df[category_df['Group'] == group]
                    group_max[group] = group_df['MedP(Cat)'].max()
                category_df['__GROUP_MAX__'] = category_df.apply(lambda row: group_max[row['Group']], axis=1)
                category_df['NYC AIR'] = category_df['MedP(Cat)'] / category_df['__GROUP_MAX__']
                category_df.drop(columns=['__GROUP_MAX__'], inplace=True)
                return category_df
                        
            elif categorization == 'intersectional':

                intersectional_df = pd.DataFrame(columns=["Intersectional Category", "N(Cat)", "MedPos(Cat)", "MedP(Cat)"])
                combo_ttl = {}
                combo_medpos = {}
                combo_medp = {}
                set_of_categorys = [ self.gender_labels, self.race_labels ]
                for combo in itertools.product(*set_of_categorys):
                    category_list = [x for x in combo]
                    category_list.reverse()
                    intersectional_category = " ".join(category_list)
                    combo_id = "::".join(combo)
                    filters = []
                    for category in combo:
                        filter = self.dataset[category] == 1
                        filters.append(filter)
                    intersection = np.logical_and(*filters)
                    intersection_med = np.logical_and(intersection, self.dataset[self.model_output_label] > value_med)
                    combo_ttl[combo_id] = self.dataset[intersection].shape[0]
                    combo_medpos[combo_id] = self.dataset[intersection_med].shape[0]
                    if combo_ttl[combo_id] > 0:
                        combo_medp[combo_id] = combo_medpos[combo_id] / combo_ttl[combo_id]
                    else:
                        raise Exception(f"No observations were found in the dataset for the intersectional demographic category {intersectional_category}")
                    df_row_dict = {
                        'Intersectional Category': intersectional_category,
                        'N(Cat)': combo_ttl[combo_id],
                        'MedPos(Cat)': combo_medpos[combo_id],
                        'MedP(Cat)': combo_medp[combo_id],
                    }
                    intersectional_df = pd.concat((intersectional_df, pd.DataFrame([df_row_dict])), axis=0, ignore_index=True)
                intersectional_max = intersectional_df['MedP(Cat)'].max()
                intersectional_df['NYC AIR'] = intersectional_df['MedP(Cat)'] / intersectional_max
                return intersectional_df

            else:

                raise Exception(f"Categorization [{categorization}] not recognized") 

        else:

            raise Exception(f"Model output type [{self.output_type}] not recognized") 

    def predicted_positive_ratio(self, category: str=None, boolean_array: np.array=None) -> tuple:

        if category is not None:
            dataset = self.dataset[self.dataset[category] == 1].copy(deep=True)
        elif boolean_array is not None:
            dataset = self.dataset[boolean_array].copy(deep=True)
        else:
            raise Exception(f"The category and boolean_array arguments cannot both be null (None)")

        total = dataset.shape[0]
        num_pos = dataset[dataset[self.model_output_label] == 1].shape[0]  # numerator for AIR

        if total > 0:
            return (total, num_pos, num_pos / total)
        else:
            raise Exception(f"No observations were found in the dataset for the demographic category {category}")

    def format_results_table(self, results_table: pd.DataFrame = None, categorization: str = None):

        formatted_results_table = results_table.copy(deep=True)

        for column in ['N(Cat)', 'Pos(Cat)', 'MedPos(Cat)']:
            if column in formatted_results_table.columns:
                formatted_results_table[column] = formatted_results_table[column].map(lambda x: np.nan if pd.isna(x) else round(x))
                formatted_results_table.astype({column: 'Int64'})

        for column in ['P(Cat)', 'MedP(Cat)']:
            if column in formatted_results_table.columns:
                formatted_results_table[column] = formatted_results_table[column].map(lambda x: "{percent:,.1f}%".format(percent=100*x))

        if self.output_type == 'binary':

            column_aliases = {
                "N(Cat)": "# of Applicants<br><small>[A]</small>", 
                "Pos(Cat)": "# Selected<br><small>[B]</small>", 
                "P(Cat)": "Selection Rate<br><small>[C]=[B]/[A]</small>", 
                "NYC AIR": "Impact Ratio<br><small>[C]/max([C])</small>"
            }
            for column in column_aliases:
                if column in results_table.columns:
                    formatted_results_table.rename(columns={column: column_aliases[column]}, inplace=True)

        elif self.output_type == 'continuous':

            formatted_results_table.drop(columns=['N(Cat)'], inplace=True)
            formatted_results_table.drop(columns=['MedPos(Cat)'], inplace=True)
            column_aliases = {
                "MedP(Cat)": "Scoring Rate<br><small>[A]</small>", 
                "NYC AIR": "Impact Ratio<br><small>[A]/max([A])</small>"
            }
            for column in column_aliases:
                if column in results_table.columns:
                    formatted_results_table.rename(columns={column: column_aliases[column]}, inplace=True)

        else:

            raise Exception(f"Model output type [{self.output_type}] not recognized") 

        return formatted_results_table
