import datetime
import uuid

from bson.binary import Binary
from gridfs.synchronous.grid_file import GridFS
from pymongo import ASCENDING, InsertOne, UpdateOne, ReplaceOne, DeleteOne

from database.mongo_db_connection import MongoUnitOfWork


def perform_insert_operations():
    collection_name = "quick_base"
    client, db = MongoUnitOfWork().mdb_connection()
    # Always drop collection before creating and adding data.
    db.drop_collection(collection_name)
    collection = db[collection_name]

    index_result_1 = collection.create_index([("uuid", ASCENDING)], unique=True)
    print("index_result_1 => ", index_result_1)
    index_result_2 = collection.create_index([("first_name", "text")])
    print("index_result_2 => ", index_result_2)

    print(f"Collection {collection_name} have following indexes: {sorted(list(collection.index_information()))}")

    # Insert a document
    data_1 = {
        "uuid": str(uuid.uuid4()),
        "first_name": "Rahul",
        "last_name": "Suthar",
        "age": 23,
        "address": {
            "city": "Ahmedabad",
            "zip": "382350"
        },
        "hobbies": ["Cricket", "chess"],
        "scores": [65, 75],
        "is_active": True,
        "joining_date": datetime.datetime(2024, 11, 12, 11, 14),
    }

    res_1 = collection.insert_one(data_1)
    print("res_1 => ", res_1)
    print("data_1 => ",
          data_1)  # NOTE: if '_id' not passed to data, then insert will add the generated id with '_id' in data.

    bulk_data = [
        {
            "uuid": str(uuid.uuid4()),
            "first_name": "Adam",
            "last_name": "Milne",
            "age": None,
            "address": {
                "city": "London",
                "zip": "335500"
            },
            "hobbies": ["Cricket"],  # check query of lowercase
            "scores": [80],  # check query of lowercase
            "is_active": False,
            "joining_date": datetime.datetime(2022, 1, 25, 16, 50),
            "metadata": {
                "preferences": {
                    "email_notifications": True,
                    "sms_notifications": False
                },
                "tags": ["premium", "trial"]
            }
        },
        {
            "uuid": str(uuid.uuid4()),
            "first_name": "Alice",
            "last_name": "Johnson",
            "age": 35,
            "address": {
                "city": "Taxas",
                "zip": "665632"
            },
            "hobbies": ["Dancing", "Singing"],
            "scores": [40, 95],
            "is_active": True,
            "joining_date": datetime.datetime(2019, 6, 20, 6, 00),
            "metadata": {
                "preferences": {},
                "tags": ["premium"]
            }
        }
    ]
    res_2 = collection.insert_many(bulk_data)
    print("res_2 => ", res_2)
    print("bulk_data => ", bulk_data)

    # NOTE: For backup and restore the database dump, use following command
    # mongodump --archive="<Archive Folder Name>" --db=<DB Name>
    # mongorestore --archive="<Archive Folder Name>" --nsFrom="<Old DB Name>.*" --nsTo="<New DB Name>.*"


def perform_query_operations():
    # NOTE: For lowercase search, we have to use regex

    collection_name = "quick_base"
    client, db = MongoUnitOfWork().mdb_connection()
    collection = db[collection_name]

    ASC_SORT = 1  # noqa
    DESC_SORT = -1  # noqa

    # Retrieve all documents
    query = collection.find()
    result = list(query)

    total_qs_count = collection.count_documents({})
    print(f"All documents fetched => {[res for res in result]} \n")
    print(f"All documents count => {len(result)} \n")
    print(f"Count Documents count => {total_qs_count} \n")

    # Fetch specified columns
    query = collection.find({}, {"_id": 0, "uuid": 1, "first_name": 1})  # 0 for exclude field, 1 for include field
    result = list(query)
    print(f"Fetch specified columns => {[res for res in result]} \n")

    # Fetch from specified column
    query = collection.find({"age": {"$gte": 30}}, {"_id": 0, "first_name": 1, "age": 1})
    result = list(query)
    print(f"Fetch from specified column => {[res for res in result]} \n")

    # Sort by a specified field
    # NOTE: 1 for ascending and -1 for descending

    query = collection.find({}, {"_id": 0, "first_name": 1, "age": 1}).sort("age", DESC_SORT)
    result = list(query)
    print(f"Sort by a specified field => {[res for res in result]} \n")

    # Find by nested document field
    query = collection.find({"address.city": "Taxas"}, {"_id": 0, "first_name": 1})
    result = list(query)
    print(f"Find by nested document field => {[res for res in result]} \n")

    # Find by type, like having null
    query = collection.find({"age": {"$type": "null"}}, {"_id": 0, "first_name": 1})
    result = list(query)
    print(f"Find by type, like having null => {[res for res in result]} \n")

    # Find by exists, like checking the nested key
    query = collection.find({"metadata": {"$exists": True}}, {"_id": 0, "first_name": 1})
    result = list(query)
    print(f"Find by exists, like checking the nested key => {[res for res in result]} \n")

    # Find by elemMatch, like values check greater, less, equal than
    # valid comparisons are: gte, lte, lt, gt and eq
    query = collection.find({"scores": {"$elemMatch": {"$eq": 80}}}, {"_id": 0, "first_name": 1})
    result = list(query)
    print(f"Find by elemMatch, like values check greater than => {[res for res in result]} \n")

    # Pagination
    query = collection.find({}, {"_id": 0, "first_name": 1}).skip(1).limit(1)
    result = list(query)
    print(f"Pagination => {[res for res in result]} \n")

    # OR condition
    query = collection.find({
        "$or": [
            {"age": {"$gte": 35}},
            {"hobbies": {"$in": ["Cricket"]}}
        ]
    }, {"_id": 0, "first_name": 1})
    result = list(query)
    print(f"OR condition => {[res for res in result]} \n")

    # AND condition
    query = collection.find({
        "$and": [
            {
                "$or": [
                    {"age": {"$gte": 30}},
                    {"age": {"$type": "null"}},
                ]
            },
            {
                "hobbies": {"$in": ["Cricket"]}
            }
        ]
    }, {"_id": 0, "first_name": 1})
    result = list(query)
    print(f"AND condition => {[res for res in result]} \n")

    # All query for array
    query = collection.find({"hobbies": ["Cricket", "Dancing"]}, {"_id": 0, "first_name": 1})
    result = list(query)
    print(f"All query for array => {[res for res in result]} \n")

    # NOT condition
    query = collection.find({"is_active": {"$not": {"$eq": False}}}, {"_id": 0, "first_name": 1})
    result = list(query)
    print(f"NOT condition => {[res for res in result]} \n")

    # Unwind: This will create new document in response for each array object with value
    # Destruct an array field into individual document.

    pipeline = [{"$unwind": "$hobbies"}]
    query = collection.aggregate(pipeline)
    result = list(query)
    print(f"NOT condition => {[res for res in result]} \n")

    # Group By
    pipeline = [
        {"$unwind": "$scores"},
        {
            "$group": {
                "_id": "$age",
                "average_score": {"$avg": "$scores"},
                "scores_sum": {"$sum": "$scores"}
            }
        }
    ]
    query = collection.aggregate(pipeline)
    result = list(query)
    print(f"Group By => {[res for res in result]} \n")

    # Filter with aggregate
    pipeline = [
        {"$match": {"is_active": True}},
        {"$unwind": "$scores"},
        {
            "$group": {
                "_id": "$age",
                "average_score": {"$avg": "$scores"},
                "scores_sum": {"$sum": "$scores"}
            }
        }
    ]
    query = collection.aggregate(pipeline)
    result = list(query)
    print(f"Filter with aggregate => {[res for res in result]} \n")

    # Text Search
    # NOTE: To use this search, we must have one text index in collection

    query = collection.find({"$text": {"$search": "Adam"}}, {"_id": 0, "first_name": 1, "uuid": 1})
    result = list(query)
    print(f"Text Search => {[res for res in result]} \n")


def perform_modify_operation():
    collection_name = "quick_base"
    client, db = MongoUnitOfWork().mdb_connection()
    collection = db[collection_name]

    # Update single document, Only update the first document
    result = collection.update_one(
        {"age": {"$type": "null"}},  # Filter Condition
        {"$set": {"age": 30}}  # Update Values
    )
    print(f"Update single document => ", result)

    # Update Many Document

    result = collection.update_many(
        {"is_active": True},
        {"$set": {"is_active": False}}
    )
    print(f"Update Many Document => ", result)

    # Update with upsert

    result = collection.update_one(
        {"age": {"$eq": 90}},
        {"$set": {"is_active": True, "first_name": "David"}},
        upsert=True,  # If no document found with filter, then add new document with data.
    )
    print(f"Update with upsert => ", result)

    # Delete One

    result = collection.delete_one(
        {"first_name": "David"},  # Delete newly created object above
    )
    print(f"Delete One => ", result)

    # Delete Many

    result = collection.delete_many(
        {"is_active": True},
    )
    print(f"Delete Many => ", result)

    # Delete All

    result = collection.delete_many({})
    print(f"Delete All => ", result)

    # Bulk Write Operation

    collection_name = "bulk_write_test"
    db.drop_collection(collection_name)
    collection = db[collection_name]

    collection.insert_one({"_id": 1, "first_name": "Smith", "age": 25})
    collection.insert_one({"_id": 2, "first_name": "Chris", "age": 42})
    collection.insert_one({"_id": 3, "first_name": "Shane", "age": 35})

    # NOTE:
    # UpdateOne will update the specific fields and not remove the fields, if skipped from document
    # ReplaceOne will completely replace the new document body with existing body.

    query = [
        InsertOne({"_id": 4, "first_name": "David", "age": 30}),
        UpdateOne({"_id": 1}, {"$set": {"age": 40}}),  # It update the contains, not remove if others key skips
        ReplaceOne({"_id": 2}, {"_id": 2, "name": "Chris", "dob": "2001-01-01"}),
        DeleteOne({"_id": 3})
    ]

    result = collection.bulk_write(query)
    print(f"Bulk Write Operation => ", result)


def perform_GridFS():
    """
    For storing files we can use GridFS or Binary data.
    If file size is smaller (under 16 MB) then we can use Binary data,
    and if file size is exceeding 16 MB then we can use GridFS.
    """
    collection_name = "quick_base_binary_files"  # New collection for Files data store
    client, db = MongoUnitOfWork().mdb_connection()
    db.drop_collection(collection_name)
    collection = db[collection_name]

    file_path = "/home/mind/Source/quick_base_backend/sample_file.pdf"

    with open(file_path, "rb") as f:
        binary_data = Binary(f.read())

    file_payload = {
        "file_name": "Sample_File.pdf",
        "data": binary_data
    }

    # Insert using Binary Data
    result = collection.insert_one(file_payload)
    print("Insert using Binary Data => ", result)

    # Fetch Binary Data using _id
    query = collection.find({"_id": file_payload.get("_id")})
    result = list(query)
    print("Fetch Binary Data using _id", result[0].get("file_name"))

    # Using GridFS
    db.drop_collection("fs.chunks")
    db.drop_collection("fs.files")
    grid_fs = GridFS(db)

    # We can pass collection name in GridFS, and it will create two new collection
    # <collection name>.files have the files data and _id except the file content read.
    # <collection name>.chunks which store the data of chunks of file and have reference to _id from files.

    with open(file_path, "rb") as f:
        file_id = grid_fs.put(
            f,
            file_name="Sample_File.pdf",
            content_type="application/pdf",
            metadata={"author": "RS", "description": "Sample file"}
        )

    print("Using GridFS file_id => ", file_id)

    query = grid_fs.find_one({"file_name": "Sample_File.pdf"})
    if query:
        content = query.read()
        with open("retrieve_sample_file.pdf", "wb") as f:
            f.write(content)
