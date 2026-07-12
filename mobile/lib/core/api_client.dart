import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiClient {
  ApiClient._();

  static final ApiClient instance = ApiClient._();

  static const _storage = FlutterSecureStorage();
  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api',
  );

  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      contentType: 'application/json',
    ),
  )..interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.read(key: 'access_token');
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
      ),
    );

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post('/token/', data: {
      'email': email,
      'password': password,
    });

    await _persistTokens(response.data['access'], response.data['refresh']);
    return response.data;
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String username,
    required String password,
    required String password2,
    required String phone,
  }) async {
    final response = await _dio.post('/auth/register/', data: {
      'email': email,
      'username': username,
      'password': password,
      'password2': password2,
      'phone': phone,
    });

    return response.data;
  }

  Future<List<Map<String, dynamic>>> fetchChildren() async {
    final response = await _dio.get('/auth/children/');
    if (response.data is List) {
      return List<Map<String, dynamic>>.from(response.data);
    }
    return [];
  }

  Future<Map<String, dynamic>> createChild({
    required String name,
    required String dateOfBirth,
    required String gender,
    required String notes,
  }) async {
    final response = await _dio.post('/auth/children/', data: {
      'name': name,
      'date_of_birth': dateOfBirth,
      'gender': gender,
      'notes': notes,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> fetchChecklist(int age) async {
    final response = await _dio.get('/milestones/checklist/', queryParameters: {'age': age});
    return response.data;
  }

  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  Future<String?> getStoredToken() async {
    return _storage.read(key: 'access_token');
  }

  Future<void> _persistTokens(String access, String refresh) async {
    await _storage.write(key: 'access_token', value: access);
    await _storage.write(key: 'refresh_token', value: refresh);
  }

  String getErrorMessage(Object error) {
    if (error is DioException) {
      final data = error.response?.data;
      if (data is Map<String, dynamic>) {
        return data.values.join(' ').toString();
      }
      if (data is String && data.isNotEmpty) {
        return data;
      }
      return error.message ?? 'Request failed';
    }
    return error.toString();
  }
}
