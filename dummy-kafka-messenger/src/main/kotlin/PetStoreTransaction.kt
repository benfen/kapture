import kotlinx.serialization.Serializable

@Serializable
data class Coordinate(val first: Double, val second: Double)

@Serializable
data class PersonName(val first: String, val second: String)

@Serializable
data class Location(val state: String,
                    val coordinates: Coordinate,
                    val city: String,
                    val zipcode: String,
                    val medianHouseholdIncome: Int,
                    val population: Int)

@Serializable
data class Customer(val id: String,
                     val name: PersonName,
                     val location: Location)

@Serializable
data class Store(val id: Int,
                 val name: String,
                 val location: Location)

@Serializable
data class Product(val fieldNames: Array<String>)

@Serializable
data class PetStoreTransaction(val id: String,
                               val dateTime: Double,
                               val customer: Customer,
                               val store: Store,
                               val products: Array<Product>)