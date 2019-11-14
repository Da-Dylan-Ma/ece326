# coverage run --source orm test_orm.py
# coverage report -m
# coverage html
# possible integration with TravisCI

import unittest
import orm
import schema
import struct
from schema import *

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
        self.user_data_1 = ("Jay", "Sung", 5.5, 31)
        self.user_data_2 = ("Issac", "Sng", 6.2, 24)
        self.user_data_3 = ("Jacob", "Kodvich", 6.0, 18)

    def tearDown(self):
        self.db.close()

    def test_Database_insert(self):
        InvalidReference = orm.exceptions.InvalidReference # BAD_FOREIGN
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW
        try:
            pk, version = self.db.insert("User", self.user_data_1)
            pk_acc, version_acc = self.db.insert("Account", [pk, "deposit", 0.0])
        except InvalidReference as e:
            self.fail("db.insert() raised {} unexpectedly!".format(type(e).__name__))

        self.assertRaises(ValueError, self.db.insert, "User2", self.user_data_1)
        self.assertRaises(ValueError, self.db.insert, "User", ("wrong argc",))
        self.assertRaises(ValueError, self.db.insert, "User", ["Issac", "Sng", 6.2, 24.0]) # float -> int
        self.assertRaises(InvalidReference, self.db.insert, "Account", [9999999999, "deposit", 0.0])

    def test_Database_update(self):
        ObjectDoesNotExist = orm.exceptions.ObjectDoesNotExist # NOT_FOUND
        InvalidReference = orm.exceptions.InvalidReference # BAD_FOREIGN
        TransactionAbort = orm.exceptions.TransactionAbort # TXN_ABORT
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW
        try:
            pk, version = self.db.insert("User", self.user_data_1)
            pk_acc, version_acc = self.db.insert("Account", [pk, "deposit", 0.0])
            version_atomic = self.db.update("User", pk, self.user_data_2, version=version)
            self.assertEqual(version_atomic, version+1)
            version = self.db.update("User", pk, self.user_data_3)
            self.assertEqual(version, version_atomic+1)
        except (ObjectDoesNotExist, InvalidReference, TransactionAbort) as e:
            self.fail("db.update() raised {} unexpectedly!".format(type(e).__name__))

        self.assertRaises(ValueError, self.db.update, "User2", pk, self.user_data_2)
        self.assertRaises(ValueError, self.db.update, "User", "1", self.user_data_2)
        self.assertRaises(ValueError, self.db.update, "User", "1", ("wrong argc",))
        self.assertRaises(ValueError, self.db.update, "User", pk, ["Issac", "Sng", 6.2, 24.0]) # float -> int
        self.assertRaises(InvalidReference, self.db.update, "Account", pk_acc, [9999999999, "deposit", 0.0])
        self.assertRaises(ObjectDoesNotExist, self.db.update, "User", 9999999999, self.user_data_2)
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

        self.assertRaises(ValueError, self.db.get, "User2", pk)
        self.assertRaises(ValueError, self.db.get, "User2", "1")
        self.assertRaises(ObjectDoesNotExist, self.db.get, "User", 9999999999)

    def test_Database_drop(self):
        ObjectDoesNotExist = orm.exceptions.ObjectDoesNotExist # NOT_FOUND
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW

        # regular entry drop
        pk, version = self.db.insert("User", self.user_data_1)
        self.db.drop("User", pk)
        self.assertRaises(ObjectDoesNotExist, self.db.get, "User", pk)

        # cascaded entry drop
        # note: foreign keys are referenced by id of row in respective table
        pk_user, version_user = self.db.insert("User", self.user_data_2)
        pk_acc1, version_acc1 = self.db.insert("Account", [pk_user, "deposit", 0.0])
        pk_acc2, version_acc2 = self.db.insert("Account", [0, "deposit", 0.0])
        self.db.drop("User", pk_user)
        self.assertRaises(ObjectDoesNotExist, self.db.get, "User", pk_user)
        self.assertRaises(ObjectDoesNotExist, self.db.get, "Account", pk_acc1)
        self.db.get("Account", pk_acc2) # exists

        self.assertRaises(ObjectDoesNotExist, self.db.drop, "User", pk_user)
        self.assertRaises(ValueError, self.db.drop, "User2", pk_user)

    def test_Database_scan(self):
        PacketError = orm.exceptions.PacketError # BAD_TABLE, BAD_VALUE, BAD_ROW
        try:
            # initial variable init
            pk1, version1 = self.db.insert("User", self.user_data_1)
            pk2, version2 = self.db.insert("User", self.user_data_2)
            pk3, version3 = self.db.insert("User", self.user_data_3)
            pk_acc, version_acc = self.db.insert("Account", [pk1, "deposit", 0.0])

            # cache prior results due updating database
            results_1 = self.db.scan("User", ("firstName", orm.easydb.OP_EQ, "Jay"))
            results_2 = self.db.scan("User", ("firstName", orm.easydb.OP_EQ, "Jason"))
            results_3 = self.db.scan("User", ("firstName", orm.easydb.OP_GT, "J"))
            results_4 = self.db.scan("User", ("height", orm.easydb.OP_LT, 10.0))
            results_5 = self.db.scan("User", ("height", orm.easydb.OP_LT, 10))
            results_6 = self.db.scan("Account", ("user", orm.easydb.OP_EQ, pk1))
            results_7 = self.db.scan("Account", ("user", orm.easydb.OP_NE, pk1))

            pk1, version1 = self.db.insert("User", self.user_data_1)
            pk2, version2 = self.db.insert("User", self.user_data_2)
            pk3, version3 = self.db.insert("User", self.user_data_3)
            pk_acc, version_acc = self.db.insert("Account", [pk1, "deposit", 0.0])

            results = self.db.scan("User", ("firstName", orm.easydb.OP_EQ, "Jay"))
            self.assertEqual(len(results), 1+len(results_1))
            self.assertEqual(results[-1:], [pk1])

            results = self.db.scan("User", ("firstName", orm.easydb.OP_EQ, "Jason"))
            self.assertEqual(len(results), 0)

            results = self.db.scan("User", ("firstName", orm.easydb.OP_GT, "J"))
            self.assertEqual(len(results), 2+len(results_3))
            self.assertEqual(results[-2:], [pk1, pk3])

            results = self.db.scan("User", ("height", orm.easydb.OP_LT, 10.0))
            self.assertEqual(len(results), 3+len(results_4))
            self.assertEqual(results[-3:], [pk1, pk2, pk3])

            # integer input to fresults_1loat
            results = self.db.scan("User", ("height", orm.easydb.OP_LT, 10))
            self.assertEqual(len(results), 3+len(results_5))
            self.assertEqual(results[-3:], [pk1, pk2, pk3])

            results = self.db.scan("Account", ("user", orm.easydb.OP_EQ, pk1))
            self.assertEqual(len(results), 1)

            results = self.db.scan("Account", ("user", orm.easydb.OP_NE, pk1))
            #self.assertEqual(len(results), 0)

        except ValueError as e:
            self.fail("db.update() raised {} unexpectedly!".format(type(e).__name__))

        self.assertRaises(ValueError, self.db.scan, "User2", ("firstName", orm.easydb.OP_EQ, "Jay"))
        self.assertRaises(ValueError, self.db.scan, "User", ("firstName2", orm.easydb.OP_EQ, "Jay"))
        self.assertRaises(ValueError, self.db.scan, "User", ("firstName", "1", "Jay"))
        self.assertRaises(ValueError, self.db.scan, "User", ("firstName", orm.easydb.OP_EQ, 1.0))
        self.assertRaises(ValueError, self.db.scan, "User", ())
        self.assertRaises(ValueError, self.db.scan, "Account", ("user", orm.easydb.OP_LT, pk1))
        self.assertRaises(ValueError, self.db.scan, "User", ("age", orm.easydb.OP_EQ, 50.0)) # will it directly reject?
        self.assertRaises(ValueError, self.db.scan, "User", ("age", orm.easydb.OP_LT, 50.0)) # will it convert to float for comparisons?

class Test_init(unittest.TestCase):

    def setUp(self):
        tb1 = (("User", (("firstName", str),    # (column_name, type)
                         ("lastName", str),
                         ("height", float),
                         ("age", int))
               ),
               ("Account", (("user", "User"),   # (column_name, table_reference)
                            ("type", str),
                            ("balance", float))
               ))
        tb4 = (("User", (("firstName", str),
                         ("lastName", str),
                         ("height", float),
                         ("age", int))
               ),
               ("Cash", (("value", float),
                         ("currency", str),
                         ("owner", "User"))
               ),
               ("Account", (("user", "User"),
                            ("type", str),
                            ("balance", "Cash"))
               ))

        self.db1 = orm.easydb.Database(tb1)
        self.db4 = orm.easydb.Database(tb4)

    def test_setup(self):
        return NotImplemented

    def test_export(self):
        with open("default.txt", "r") as f:
            ans = f.read()
        test = orm.export("easydb", schema)
        self.assertEqual(ans, test)

class Test_table(unittest.TestCase):

    def setUp(self):
        self.db = orm.setup("easydb", schema)
        self.db.connect("127.0.0.1", 8080)

    def tearDown(self):
        self.db.close()

    def test_default(self):
        # User: basic table test
        joe = User(self.db, firstName="Joe", lastName="Harris", age=32)
        self.assertEqual(joe.pk, None)
        self.assertEqual(joe.height, 0.)
        joe.lastName = "Smith"
        joe.save()
        self.assertNotEqual(joe.pk, None)            # 2 (the id of the object)
        old_joe_pk = joe.pk
        self.assertEqual(joe.version, 1)      # 1 (the version of the object)
        joe.age = 33
        joe.save(atomic=False)    # disable atomic update for this call to easydb.update
        self.assertEqual(joe.version, 2)               # 2 (new version of the object)
        joe.age = 34
        joe.save()                # this will call easydb.update, which may raise TransactionAbort
        joe.delete()              # deletes the row from the database
        self.assertEqual(joe.pk, None)            # True
        joe.save()                #
        self.assertNotEqual(joe.pk, old_joe_pk)

        # Account: foreign key test
        acc = Account(self.db, user=joe)
        acc.save()

    def test_get(self):
        joe_michael = User(self.db, firstName="Joe", lastName="Michael", age=32)
        joe_michael.save()
        joe_michael_2 = User.get(self.db, joe_michael.pk)
        self.assertEqual(joe_michael.pk, joe_michael_2.pk)
        self.assertEqual(joe_michael.version, joe_michael_2.version)
        self.assertEqual(joe_michael.lastName, joe_michael_2.lastName)

    def test_filter(self):
        # Equality operator
        joe_objs = User.filter(self.db, firstName="Joe")
        joe_michael = User(self.db, firstName="Joe", lastName="Michael", age=32)
        joe_michael.save()
        more_joe_objs = User.filter(self.db, firstName="Joe")
        self.assertEqual(len(joe_objs) + 1, len(more_joe_objs))

        # Other operators
        User.filter(self.db, firstName__gt="J")
        User.filter(self.db, firstName__lt="J")
        User.filter(self.db, firstName__ne="Joe")
        User.filter(self.db, age__gt=33)

        # Add Account tests
        joe_michael = User(self.db, firstName="Joe", lastName="Michael", age=32)
        joe_michael.save()
        acc = Account(self.db, user=joe_michael)
        acc.save()
        results_1 = Account.filter(self.db, user=joe_michael)
        results_2 = Account.filter(self.db, user=joe_michael.pk)
        self.assertEqual(results_1[0].pk, results_2[0].pk)

    def test_count(self):
        # TODO: Add exception handling
        User.count(self.db, firstName__ne="Joe")
        User.count(self.db, firstName="Joe")

    def test_cascade_save(self):
        greg = User(self.db, firstName="Greg", lastName="Russell", age=27)
        account = Account(self.db, user=greg, type="Chequing", balance=100.0)
        account.save()  # will save 'greg' first before saving 'account'
        saving = Account(self.db, user=greg, type="Savings", balance=200.0)
        saving.save()   # will not save 'greg' first since it already exists in database


if __name__ == "__main__":
    unittest.main()
    db = orm.setup("easydb", schema)
    db.connect("127.0.0.1", 8080)
