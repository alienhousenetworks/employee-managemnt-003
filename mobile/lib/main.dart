import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
void main() => runApp(const AgencyWorkforceApp());
class AgencyWorkforceApp extends StatelessWidget {
  const AgencyWorkforceApp({super.key});
  @override Widget build(BuildContext context) => MaterialApp(title:'Agency Workforce OS', debugShowCheckedModeBanner:false, theme:ThemeData(colorScheme:ColorScheme.fromSeed(seedColor:const Color(0xFFB5F36B),brightness:Brightness.dark),scaffoldBackgroundColor:const Color(0xFF0B1018),useMaterial3:true),home:const LoginScreen());
}
