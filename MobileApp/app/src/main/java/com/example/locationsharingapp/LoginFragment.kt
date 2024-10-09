package com.example.locationsharingapp

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.example.locationsharingapp.databinding.FragmentLoginBinding
import com.example.locationsharingapp.network.*
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginFragment : Fragment() {

    private var _binding: FragmentLoginBinding? = null
    private val binding get() = _binding!!
    private val sharedPrefName = "user_prefs"

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLoginBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.buttonLogin.setOnClickListener {
            val username = binding.editTextUsername.text.toString().trim()
            val password = binding.editTextPassword.text.toString().trim()

            if (username.isNotEmpty() && password.isNotEmpty()) {
                loginUser(username, password)
            } else {
                Toast.makeText(
                    requireContext(),
                    "Please enter username and password",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

//        binding.buttonRegister.setOnClickListener {
//            val username = binding.editTextUsername.text.toString().trim()
//            val password = binding.editTextPassword.text.toString().trim()
//            val email = "hi1@example.com" // Replace with actual email input from the user
//
//            if (username.isNotEmpty() && password.isNotEmpty() && email.isNotEmpty()) {
//                registerUser(username, email, password)
//            } else {
//                Toast.makeText(requireContext(), "Please fill in all fields", Toast.LENGTH_SHORT)
//                    .show()
//            }
//        }
        binding.buttonRegister.setOnClickListener {
            findNavController().navigate(R.id.action_loginFragment_to_registerFragment)
        }
    }

    private fun loginUser(username: String, password: String) {
        val loginRequest = UserLoginRequest(username, password)
        RetrofitClient.apiService.loginUser(loginRequest)
            .enqueue(object : Callback<UserLoginResponse> {
                override fun onResponse(
                    call: Call<UserLoginResponse>,
                    response: Response<UserLoginResponse>
                ) {
                    if (response.isSuccessful) {
                        val loginResponse = response.body()
                        if (loginResponse != null) {
                            saveLoginStatus(true)
                            saveUserId(loginResponse.user_id)
                            Toast.makeText(
                                requireContext(),
                                loginResponse.message,
                                Toast.LENGTH_SHORT
                            ).show()
                            findNavController().navigate(R.id.action_loginFragment_to_FirstFragment)
                        } else {
                            Toast.makeText(
                                requireContext(),
                                "Login failed: empty response",
                                Toast.LENGTH_SHORT
                            ).show()
                        }
                    } else {
                        val errorBody = response.errorBody()?.string()
                        val errorMessage = parseErrorMessage(errorBody)
                        Toast.makeText(
                            requireContext(),
                            "Login failed: $errorMessage",
                            Toast.LENGTH_SHORT
                        ).show()
                        Log.e("LoginFragment", "Login error: $errorMessage")
                    }
                }

                override fun onFailure(call: Call<UserLoginResponse>, t: Throwable) {
                    Toast.makeText(
                        requireContext(),
                        "Network error: ${t.localizedMessage}",
                        Toast.LENGTH_SHORT
                    ).show()
                    Log.e("LoginFragment", "Login failure", t)
                }
            })
    }

    private fun registerUser(username: String, email: String, password: String) {
        val registerRequest = UserRegisterRequest(username, email, password)
        RetrofitClient.apiService.registerUser(registerRequest)
            .enqueue(object : Callback<UserRegisterResponse> {
                override fun onResponse(
                    call: Call<UserRegisterResponse>,
                    response: Response<UserRegisterResponse>
                ) {
                    if (response.isSuccessful) {
                        val registerResponse = response.body()
                        if (registerResponse != null) {
                            Toast.makeText(
                                requireContext(),
                                registerResponse.message,
                                Toast.LENGTH_SHORT
                            ).show()
                        } else {
                            Toast.makeText(
                                requireContext(),
                                "Registration failed: empty response",
                                Toast.LENGTH_SHORT
                            ).show()
                        }
                    } else {
                        val errorBody = response.errorBody()?.string()
                        val errorMessage = parseErrorMessage(errorBody)
                        Toast.makeText(
                            requireContext(),
                            "Registration failed: $errorMessage",
                            Toast.LENGTH_SHORT
                        ).show()
                        Log.e("LoginFragment", "Registration error: $errorMessage")
                    }
                }

                override fun onFailure(call: Call<UserRegisterResponse>, t: Throwable) {
                    Toast.makeText(
                        requireContext(),
                        "Network error: ${t.localizedMessage}",
                        Toast.LENGTH_SHORT
                    ).show()
                    Log.e("LoginFragment", "Registration failure", t)
                }
            })
    }

    private fun parseErrorMessage(errorBody: String?): String {
        return try {
            val gson = Gson()
            val errorResponse = gson.fromJson(errorBody, ErrorResponse::class.java)
            errorResponse.error
        } catch (e: JsonSyntaxException) {
            "An error occurred"
        } catch (e: Exception) {
            "An error occurred"
        }
    }

    private fun saveLoginStatus(isLoggedIn: Boolean) {
        val sharedPref = activity?.getSharedPreferences(sharedPrefName, Context.MODE_PRIVATE)
        sharedPref?.edit()?.putBoolean("is_logged_in", isLoggedIn)?.apply()
    }

    private fun saveUserId(userId: Int) {
        val sharedPref = activity?.getSharedPreferences(sharedPrefName, Context.MODE_PRIVATE)
        sharedPref?.edit()?.putInt("user_id", userId)?.apply()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}