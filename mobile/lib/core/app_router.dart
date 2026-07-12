import 'package:go_router/go_router.dart';
import '../screens/assessment_screen.dart';
import '../screens/children_screen.dart';
import '../screens/home_screen.dart';
import '../screens/login_screen.dart';
import '../screens/milestones_screen.dart';
import '../screens/register_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/login',
  routes: [
    GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
    GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
    GoRoute(path: '/', builder: (context, state) => const HomeScreen()),
    GoRoute(path: '/children', builder: (context, state) => const ChildrenScreen()),
    GoRoute(path: '/milestones', builder: (context, state) => const MilestoneChecklistScreen()),
    GoRoute(
      path: '/assessment',
      builder: (context, state) {
        final extra = state.extra as Map<String, dynamic>;
        return AssessmentScreen(
          childId: extra['childId'] as int,
          childName: extra['childName'] as String,
          childAge: extra['childAge'] as int,
        );
      },
    ),
  ],
);
