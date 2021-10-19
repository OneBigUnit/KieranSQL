from KieranSQL import SQLiteTable, String, Integer, connect_to


@SQLiteTable()
class Subjects:
  SubjectID: Integer(primary_key=True)
  SubjectName: String(20)


@SQLiteTable()
class Students:
  StudentID: Integer(primary_key=True)
  FirstName: String(30)
  LastName: String(20)
  FavouriteSubject: Subjects.SubjectID


def run():
  with connect_to(Subjects, commit=False):
    Subjects.InsertInto({
      Subjects.SubjectName: "Computing"
    })
  print(Subjects)


  with connect_to(Students):
    Students.InsertInto({
      Students.FirstName: "Kieran", 
      Students.LastName: "Lock", 
      Students.FavouriteSubject: 1})

    results = Students.Select("*").Fetch()
    print(results)

    Students.Update({
      Students.FirstName: "Connor", 
      Students.LastName: "Jackson", 
      Students.FavouriteSubject: 1
    }).Where(Students.StudentID == 1)
    
    results = Students.Select("*").Fetch()
  print(results)


if __name__ == "__main__":
  run()
