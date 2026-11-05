import importlib.util
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[1] / "scripts" / "update_epoch.py"
SPEC = importlib.util.spec_from_file_location("update_epoch", FILE)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class CSVImportTests(unittest.TestCase):
    def test_accepts_realistic_rows_with_bounds_and_date(self):
        rows = ["model,organization,eci,eci_lower,eci_upper,release_date"]
        for i in range(22):
            rows.append(f"Model {i},Example Lab,{120+i},{118+i},{122+i},2025-{(i%12)+1:02d}-10")
        models, history = mod.extract("\n".join(rows))
        self.assertEqual(len(models), 22)
        self.assertGreaterEqual(len(history), 20)
        self.assertEqual(models[0]["score"], 141)

    def test_rejects_missing_uncertainty_fields(self):
        rows = ["model,organization,eci"] + [f"Model {i},Lab,{120+i}" for i in range(22)]
        with self.assertRaises(ValueError):
            mod.extract("\n".join(rows))

    def test_rejects_changed_required_schema(self):
        with self.assertRaises(ValueError):
            mod.extract("unknown,metric\nA,1\n")

    def test_does_not_invent_release_dates(self):
        rows = ["model,organization,eci,eci_lower,eci_upper"]
        rows += [f"Model {i},Lab,{120+i},{118+i},{122+i}" for i in range(22)]
        models, history = mod.extract("\n".join(rows))
        self.assertEqual(len(models), 22)
        self.assertEqual(history, [])


if __name__ == "__main__":
    unittest.main()
