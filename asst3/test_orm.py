# coverage run --source orm test_orm.py
# coverage report -m
# coverage html
# possible integration with TravisCI

import unittest
import orm
import schema

class Test_easydb_setup(unittest.TestCase):

    def setUp(self):
        self.tb = (("User", (("firstName", str),    # (column_name, type)
                             ("lastName", str),
                             ("height", float),
                             ("age", int))
                   ),
                   ("Account", (("user", "User"),   # (column_name, table_reference)
                                ("type", str),
                                ("balance", float))
                   ))

    def test_Database_init(self):
        Database = orm.easydb.Database
        IntegrityError = orm.exceptions.IntegrityError
        try: # to distinguish fail/error
            Database(self.tb)
            Database([])
            Database([("User", [])])
            Database([("User", [("firstName", str)])])
        except (TypeError, ValueError, IntegrityError) as e:
            self.fail("Database(tb) raised {} unexpectedly!".format(type(e).__name__))

        self.assertRaises(TypeError, Database, [(5, [])])
        self.assertRaises(TypeError, Database, [("User", [(5, float)])])
        self.assertRaises(ValueError, Database, [("User", [("firstName", set)])])
        self.assertRaises(ValueError, Database, [("User", [("id", float)])])
        self.assertRaises(ValueError, Database, [("User", [("pk", float)])])
        self.assertRaises(IntegrityError, Database, [("User", [("firstName", "Account")])])
        self.assertRaises(IntegrityError, Database, [("User", [("firstName", "User")])])

    def test_Database_repr(self):
        self.assertEqual(str(orm.easydb.Database(self.tb)), "<EasyDB Database object>")

    def test_Database_connect(self):
        db = orm.easydb.Database(self.tb)
        db.connect("127.0.0.1", 8080)
        db.close()

class Test_easydb_interface(unittest.TestCase):

    def setUp(self):
        self.tb = (("User", (("firstName", str),    # (column_name, type)
                             ("lastName", str),
                             ("height", float),
                             ("age", int))
                   ),
                   ("Account", (("user", "User"),   # (column_name, table_reference)
                                ("type", str),
                                ("balance", float))
                   ))
        self.db = orm.easydb.Database(self.tb)
        self.db.connect("127.0.0.1", 8080)
        self.user_data_1 = ["Jay", "Sung", 5.5, 31]
        self.user_data_2 = ["Issac", "Sng", 6.2, 24]
        self.user_data_3 = ["Jacob", "Kodvich", 6.0, 18]

    def tearDown(self):
        self.db.close()

    def test_Database_insert(self):
        InvalidReference = orm.exceptions.InvalidReference # BAD_FOREIGN
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW
        try:
            pk, version = self.db.insert("User", self.user_data_1)
            pk_acc, version_acc = self.db.insert("Account", pk, "deposit", 0.0)
        except InvalidReference as e:
            self.fail("db.insert() raised {} unexpectedly!".format(type(e).__name__))

        self.assertRaises(PacketError, self.db.insert, "User2", self.user_data_1)
        self.assertRaises(PacketError, self.db.insert, "User", ("wrong argc",))
        self.assertRaises(PacketError, self.db.insert, "User", pk, ["Issac", "Sng", 6.2, 24.0]) # float -> int
        self.assertRaises(InvalidReference, self.db.insert, "Account", [99, "deposit", 0.0])

    def test_Database_update(self):
        ObjectDoesNotExist = orm.exceptions.ObjectDoesNotExist # NOT_FOUND
        InvalidReference = orm.exceptions.InvalidReference # BAD_FOREIGN
        TransactionAbort = orm.exceptions.TransactionAbort # TXN_ABORT
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW
        try:
            pk, version = self.db.insert("User", self.user_data_1)
            pk_acc, version_acc = self.db.insert("Account", pk, "deposit", 0.0)
            version_atomic = self.db.update("User", pk, self.user_data_2, version=version)
            self.assertNotEqual(version_atomic, version)
            version = self.db.update("User", pk, self.user_data_3)
            self.assertEqual(version, 0)
        except (ObjectDoesNotExist, InvalidReference, TransactionAbort) as e:
            self.fail("db.update() raised {} unexpectedly!".format(type(e).__name__))

        self.assertRaises(PacketError, self.db.update, "User2", pk, self.user_data_2)
        self.assertRaises(PacketError, self.db.update, "User", "1", self.user_data_2)
        self.assertRaises(PacketError, self.db.update, "User", "1", ("wrong argc",))
        self.assertRaises(PacketError, self.db.update, "User", pk, ["Issac", "Sng", 6.2, 24.0]) # float -> int
        self.assertRaises(InvalidReference, self.db.update, "Account", pk_acc, [99, "deposit", 0.0])
        self.assertRaises(ObjectDoesNotExist, self.db.update, "User", pk, self.user_data_2)
        self.assertRaises(TransactionAbort, self.db.update, "User", pk, self.user_data_2, version=version_atomic) # fails since non-atomic changes version number

    def test_Database_get(self):
        ObjectDoesNotExist = orm.exceptions.ObjectDoesNotExist # NOT_FOUND
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW
        try:
            pk, version = self.db.insert("User", self.user_data_1)
            values, version = self.db.get("User", pk)
            self.assertEqual(values, self.user_data_1)
        except ObjectDoesNotExist as e:
            self.fail("db.update() raised {} unexpectedly!".format(type(e).__name__))

        self.assertRaises(PacketError, self.db.get, "User2", pk)
        self.assertRaises(PacketError, self.db.get, "User2", "1")
        self.assertRaises(ObjectDoesNotExist, self.db.get, "User", 99)

    def test_Database_drop(self):
        ObjectDoesNotExist = orm.exceptions.ObjectDoesNotExist # NOT_FOUND
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW

        # regular entry drop
        pk, version = self.db.insert("User", self.user_data_1)
        self.db.drop("User", pk)
        self.assertRaises(ObjectDoesNotExist, self.db.get, "User", pk_user)

        # cascaded entry drop
        # note: foreign keys are referenced by id of row in respective table
        pk_user, version_user = self.db.insert("User", self.user_data_2)
        pk_acc1, version_acc1 = self.db.insert("Account", pk_user, "deposit", 0.0)
        pk_acc2, version_acc2 = self.db.insert("Account", 0, "deposit", 0.0)
        self.db.drop("User", pk_user)
        self.assertRaises(ObjectDoesNotExist, self.db.get, "User", pk_user)
        self.assertRaises(ObjectDoesNotExist, self.db.get, "Account", pk_acc1)
        self.db.get("Account", pk_acc2) # exists

        self.assertRaises(ObjectDoesNotExist, self.db.drop, "User", pk_user)
        self.assertRaises(PacketError, self.db.drop, "User2", pk_user)

    def test_Database_scan(self):
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW
        try:
            pk1, version1 = self.db.insert("User", self.user_data_1)
            pk2, version2 = self.db.insert("User", self.user_data_2)
            pk3, version3 = self.db.insert("User", self.user_data_3)
            pk_acc, version_acc = self.db.insert("Account", pk1, "deposit", 0.0)

            results = db.scan("User", ("firstName", orm.easydb.OP_EQ, "Jay"))
            self.assertEqual(len(results), 1)
            self.assertEqual(results, [pk1])

            results = db.scan("User", ("firstName", orm.easydb.OP_EQ, "Jason"))
            self.assertEqual(len(results), 0)

            results = db.scan("User", ("firstName", orm.easydb.OP_GT, "J"))
            self.assertEqual(len(results), 2)
            self.assertEqual(results, [pk1, pk3])

            results = db.scan("User", ("height", orm.easydb.OP_LT, 10.0))
            self.assertEqual(len(results), 3)
            self.assertEqual(results, [pk1, pk2, pk3])

            # integer input to float
            results = db.scan("User", ("height", orm.easydb.OP_LT, 10))
            self.assertEqual(len(results), 3)
            self.assertEqual(results, [pk1, pk2, pk3])

            results = db.scan("Account", ("user", orm.easydb.OP_EQ, pk1))
            self.assertEqual(len(results), 1)
            self.assertEqual(results, [pk1])

            results = db.scan("Account", ("user", orm.easydb.OP_NE, pk1))
            self.assertEqual(len(results), 0)

        except ValueError as e:
            self.fail("db.update() raised {} unexpectedly!".format(type(e).__name__))

        self.assertRaises(PacketError, self.db.scan, "User2", ("firstName", orm.easydb.OP_EQ, "Jay"))
        self.assertRaises(PacketError, self.db.scan, "User", ("firstName2", orm.easydb.OP_EQ, "Jay"))
        self.assertRaises(PacketError, self.db.scan, "User", ("firstName", "1", "Jay"))
        self.assertRaises(PacketError, self.db.scan, "User", ("firstName", orm.easydb.OP_EQ, 1.0))
        self.assertRaises(PacketError, self.db.scan, "User", ())
        self.assertRaises(PacketError, self.db.scan, "Account", ("user", orm.easydb.OP_LT, pk1))
        self.assertRaises(PacketError, self.db.scan, "User", ("age", orm.easydb.OP_EQ, 50.0)) # will it directly reject?
        self.assertRaises(PacketError, self.db.scan, "User", ("age", orm.easydb.OP_LT, 50.0)) # will it convert to float for comparisons?


if __name__ == "__main__":
    unittest.main()