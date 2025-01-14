# Generic imports
from statistics import mean
import pandas as pd

# Local imports
import core.utils.rest_api
import dashboard.utils.generic_graphic_data
import dashboard.utils.plotly
import dashboard.utils.generic_process_data


def sequencing_graphics():
    def get_pre_proc_data(graphic_name, out_format):
        """Get the pre-processed data for the graphic name.
        If there is not data stored for the graphic, it will query to store
        them before calling for the second time
        """
        json_data = dashboard.utils.generic_graphic_data.get_graphic_json_data(
            graphic_name
        )
        if json_data is None:
            # Execute the pre-processed task to get the data
            if graphic_name == "library_kit_pcr_1":
                result = (
                    dashboard.utils.generic_process_data.pre_proc_library_kit_pcr_1()
                )
            elif graphic_name == "ct_number_of_base_pairs_sequenced":
                result = (
                    dashboard.utils.generic_process_data.pre_proc_based_pairs_sequenced()
                )
            else:
                return {"ERROR": "pre-processing not defined"}
            if "ERROR" in result:
                return result
            json_data = dashboard.utils.generic_graphic_data.get_graphic_json_data(
                graphic_name
            )
        if out_format == "list_of_dict":
            data = []
            for key, values in json_data.items():
                # Convert string to float values
                tmp_data = []
                for str_val, numbers in values.items():
                    try:
                        float_val = float(str_val)
                    except ValueError:
                        continue
                    tmp_data += [float_val] * numbers
                data.append({key: tmp_data})
        else:
            data = {"based": [], "cts": []}
            for key, values in json_data.items():
                data["based"].append(int(key))
                data["cts"].append(mean(values))
        return data

    def fetch_sequencing_data(project_field, columns):
        # get stats utilization fields from LIMS
        lims_data = core.utils.rest_api.get_stats_data(
            {
                "sample_project_name": "Relecov",
                "project_field": project_field,
            }
        )
        if "ERROR" in lims_data:
            return lims_data
        return pd.DataFrame(lims_data.items(), columns=columns)

    sequencing = {}
    inst_platform_df = fetch_sequencing_data(
        project_field="sequencing_instrument_platform",
        columns=["instrument_platform", "number"],
    )
    if "ERROR" in inst_platform_df:
        return inst_platform_df
    sequencing["instrument_platform"] = dashboard.utils.plotly.bar_graphic(
        data=inst_platform_df,
        col_names=["instrument_platform", "number"],
        legend=[""],
        yaxis={"title": "Number of samples"},
        options={"title": "Instrument platform", "height": 400},
    )
    inst_model_df = fetch_sequencing_data(
        project_field="sequencing_instrument_model",
        columns=["instrument_model", "number"],
    )
    sequencing["instrument_model"] = dashboard.utils.plotly.bar_graphic(
        data=inst_model_df,
        col_names=["instrument_model", "number"],
        legend=[""],
        yaxis={"title": "Number of samples"},
        options={"title": "Instrument model", "height": 400},
    )
    lib_preparation_df = fetch_sequencing_data(
        project_field="library_preparation_kit",
        columns=["library_preparation", "number"],
    )
    sequencing["library_preparation"] = dashboard.utils.plotly.bar_graphic(
        data=lib_preparation_df,
        col_names=["library_preparation", "number"],
        legend=[""],
        yaxis={"title": "Number of samples"},
        options={"title": "Library preparation", "height": 400},
    )
    read_length_df = fetch_sequencing_data(
        project_field="read_length",
        columns=["read_length", "number"],
    )
    sequencing["read_length"] = dashboard.utils.plotly.bar_graphic(
        data=read_length_df,
        col_names=["read_length", "number"],
        legend=[""],
        yaxis={"title": "Number of samples"},
        options={"title": "Read length", "height": 400, "colors": "#1aff8c"},
    )
    # box plot for library preparation kit

    cts_library_data = get_pre_proc_data("library_kit_pcr_1", "list_of_dict")
    sequencing["cts_library"] = dashboard.utils.plotly.box_plot_graphic(
        cts_library_data,
        {
            "title": "Boxplot Cts / Library preparation kit",
            "height": 400,
            "width": 420,
        },
    )

    cts_pcr_1 = get_pre_proc_data("ct_number_of_base_pairs_sequenced", "dict")
    sequencing["number_of_base"] = dashboard.utils.plotly.line_graphic(
        cts_pcr_1["based"],
        cts_pcr_1["cts"],
        {
            "title": "CTs / Base pairs sequenced",
            "height": 350,
            "width": 300,
            "x_title": "Number of base pairs sequenced",
            "y_title": "PCR CT 1",
        },
    )
    return sequencing
