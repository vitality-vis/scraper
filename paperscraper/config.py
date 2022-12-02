from datetime import datetime
from pathlib import Path
from typing import Union


class Config:
    """The main config object."""
    def __init__(self, root_dir: Union[str, Path] = None,
                 assets_dir: Union[str, Path] = None,
                 output_dir: Union[str, Path] = None):
        """Initialize the config."""
        if root_dir is None:
            _root_dir = Path(__file__).parent.parent
        else:
            _root_dir = Path(root_dir)

        if assets_dir is None:
            assets_dir = _root_dir / "assets"
        elif not isinstance(assets_dir, Path):
            assets_dir = Path(assets_dir)

        if output_dir is None:
            output_dir = _root_dir / "output"
        elif not isinstance(output_dir, Path):
            assets_dir = Path(output_dir)

        # TODO: [Update as required] Paths to important input/output files
        # FIXME: automatically extract the latest
        self.path_input_raw = assets_dir / "data" / "dblp-2022-11-02.xml"
        self.path_input = assets_dir / "data" / "dblp_processed.xml"
        self.path_output = output_dir / "output.db"
        self.path_postprocessing_output = output_dir / "output_processed.tsv"
        self.path_unique_venues = output_dir / "unique_venues.db"
        self.path_unique_keywords = output_dir / "unique_keywords.tsv"
        self.path_unique_authors = output_dir/ "unique_authors.tsv"

        datetime_str = f"{datetime.now():%Y-%m-%d_%H-%M-%S%z}"
        self.path_logfile = output_dir / f"log-{datetime_str}.tsv"
        self.path_console_log_file = output_dir / f"console-{datetime_str}.log"

        # ChromeDriver
        # TODO Option 1: Manual Download  from https://chromedriver.chromium.org/downloads (e.g., ChromeDriver 86.0.4240.22) and save to a known location in PATH
        # TODO Option 2: Install using brew: `brew cask install chromedriver`. It is generally saved to `/usr/local/bin/chromedriver`
        # For Mac OSX, the executable will have to be quarantined - `xattr -d com.apple.quarantine chromedriver`
        # Set the chromedriver path below.
        self.path_chromedriver = assets_dir / "chromedriver"  # /usr/local/bin/chromedriver

        # ChromeOptions binary
        # TODO: [Update this path depending on where it is located in your Operating System]
        self.path_chromeoptions_binary = Path("/") / "Applications" / "Google Chrome.app" / "Contents" / "MacOS" / "Google Chrome"

        # List of Venues we target with their DBLP category. This information can be found in the <path_unique_venues> path above.
        # TODO: [Update as required] Don't forget to add the corresponding logic to scrape keywords/absracts/titles/citations, etc.
        self.interesting_venues = {
            "ACM Trans. Comput. Hum. Interact.": {
                "sourcetype": "journal",
                "publishers": ["acm_digital_library"]
            },
            "AVI": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "BCS HCI": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library", "scienceopen", "springer_v2"]
            },
            "BCS HCI (1)": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "BCS HCI (2)": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "BELIV": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library", "ieee_explore"]
            },
            "BioVis": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "CHI": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "Cognitive Biases in Visualizations": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2"]
            },
            "CogSci": {
                "sourcetype": "booktitle",
                "publishers": ["cogsci"]
            },
            "Comput. Graph. Forum": {
                "sourcetype": "journal",
                "publishers": ["wiley_online_library"]
            },
            "Conference on Designing Interactive Systems": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "Conference on Designing Interactive Systems (Companion Volume)": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "CSCW": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "Diagrams": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2"]
            },
            "Eurographics": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2", "eurographics_digital_library"]
            },
            "Eurographics (Areas Papers)": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library"]
            },
            "Eurographics (Posters)": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library"]
            },
            "Eurographics (Short Papers)": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library"]
            },
            "Eurographics (Short Presentations)": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library" ]
            },
            "Eurographics (State of the Art Reports)": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library" ]
            },
            "EuroVAST@EuroVis": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library"]
            },
            "Graphics Interface": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library", "graphics_interface_proceedings"]
            },
            "ICDM": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2", "ieee_explore"]
            },
            "IEEE Computer Graphics and Applications": {
                "sourcetype": "journal",
                "publishers": ["ieee_explore"]
            },
            "IEEE Trans. Vis. Comput. Graph.": {
                "sourcetype": "journal",
                "publishers": ["ieee_explore"]
            },
            "IEEE VAST": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "IEEE Visualization": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "IEEE VIS (Short Papers)": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "Information Visualization": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2", "dagstuhl"]
            },
            "INTERACT": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2"]
            },
            "INTERACT (1)": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2"]
            },
            "INTERACT (2)": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2"]
            },
            "INTERACT (3)": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2"]
            },
            "INTERACT (4)": {
                "sourcetype": "booktitle",
                "publishers": ["springer_v2"]
            },
            "International Conference on Supercomputing": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "IUI": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "IV": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "IV (1)": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "IV (2)": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "IVAPP": {
                "sourcetype": "booktitle",
                "publishers": ["scitepress"]
            },
            "J. Vis.": {
                "sourcetype": "journal",
                "publishers": ["springer_v1"]
            },
            "KDD": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library", "aaai"]
            },
            "PacificVis": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "SciVis": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "SIBGRAPI": {
                "sourcetype": "booktitle",
                "publishers": ["ieee_explore"]
            },
            "SIGGRAPH": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "SIGGRAPH Asia": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "SIGMOD Conference": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "UbiComp": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library", "springer_v2"]
            },
            "UIST": {
                "sourcetype": "booktitle",
                "publishers": ["acm_digital_library"]
            },
            "VAST": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library", "ieee_explore" ]
            },
            "VAST (Short and Project Papers)": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library", "ieee_explore" ]
            },
            "VCBM": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library"]
            },
            "Vis. Comput.": {
                "sourcetype": "journal",
                "publishers": ["springer_v1"]
            },
            "VMV": {
                "sourcetype": "booktitle",
                "publishers": ["eurographics_digital_library"]
            }
        }

        # Object to map different variations of a keyword to a consistent name.
        self.keywords_to_merge = {
            "cscw": "computer supported collaborative work",
            "computer supported collaborative work": "computer supported collaborative work",
            "data visualization": "data visualization",
            "data visualisation": "data visualization",
            "visualisation": "visualization",
            "visualization": "visualization",
            "hci": "human computer interaction",
            "human computer interaction": "human computer interaction",
            "human-computer-interaction": "human computer interaction",
            "human-computer interaction": "human computer interaction",
            "human computer interaction (hci)": "human computer interaction",
            "human-computer interaction (hci)": "human computer interaction",
            "human computer interactions": "human computer interaction",
            "human-computer-interactions": "human computer interaction",
            "human-computer interactions": "human computer interaction",
        }

        self.keyword_patterns_to_remove = [
            r"\d+.\d+.\d+.",  # e.g., 1.3.4.
            r"\d+.\d+.\d+",  # e.g., 1.3.4
            r"\w+.\d+.\d+.",  # e.g., d.3.4.
            r"\w+.\d+.\d+",  # e.g., d.3.4
            r"according to",
            r"acm ccs",
            r"acmccs",
            r"acma ccs",
            r"\(\s*\)",
            r"\/spl",
            r"\/sup",
            r"\/",
            r"^-\s*"
        ]


config = Config()
