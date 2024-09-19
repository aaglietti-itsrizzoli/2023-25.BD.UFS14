def func(x):
    return x + 1

def test_answer(snapshot):
    extract_ouput = func(23)
    snapshot.snapshot_dir = 'snapshots'  # This line is optional.
    snapshot.assert_match(str(extract_ouput), 'foo_output.txt')
