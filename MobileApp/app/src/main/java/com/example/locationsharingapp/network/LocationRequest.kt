package com.example.locationsharingapp.network

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

// Data Classes
data class UserLoginRequest(val username: String, val password: String)
data class UserRegisterRequest(val username: String, val email: String, val password: String)
data class UserLoginResponse(val message: String, val user_id: Int)
data class UserRegisterResponse(val message: String, val user_id: Int)
data class ErrorResponse(val error: String)
data class LocationRequest(val user_id: Int, val latitude: Double, val longitude: Double)

// ApiService Interface
interface ApiService {
    @POST("/login")
    fun loginUser(@Body loginRequest: UserLoginRequest): Call<UserLoginResponse>

    @POST("/user")
    fun registerUser(@Body registerRequest: UserRegisterRequest): Call<UserRegisterResponse>

    @POST("/location")
    fun sendLocation(@Body locationRequest: LocationRequest): Call<Void>
}