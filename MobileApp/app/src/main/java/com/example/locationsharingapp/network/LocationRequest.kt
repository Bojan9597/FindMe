package com.example.locationsharingapp.network

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

data class LocationRequest(
    val user_id: Int,
    val latitude: Double,
    val longitude: Double
)

interface ApiService {
    @POST("/location")
    fun sendLocation(@Body locationRequest: LocationRequest): Call<Void>
}