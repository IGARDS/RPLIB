import pathlib
DIR=pathlib.Path(__file__).parent.absolute()

# Import the student solutions
import pyrplib

RPLIB_DATA_PREFIX=f"{DIR}/../data"

def test_1():
    dataset_id =  636
    card_type = 'lop'
    rplib_data = pyrplib.data.Data(RPLIB_DATA_PREFIX)
    card = rplib_data.load_card(dataset_id,card_type)
    assert card is not None
