#include <iostream>

using namespace std;

int main() {
    // 변수를 정의할 떄 자료형을 미리 지정해야 합니다.
    // 자료형은 바꿀 수 없습니다.

    // 내부적으로 메모리를 이미 갖고 있습니다.
    int i; // 변수의 이름이 메모리 공간을 의미한다. - 주소값 대신에 인간의 언어와 비슷한 변수로 사용하게 도와주는 것이다.
    i = 123; // 변수에 값 지정 (객체 러퍼런스 아님 - 이건 무슨 말일까?) - 파이썬이 느린 이유 - 레퍼런스를 따라간다 파이썬은 - 비효율적인가봄
    // C++은 메모리 주소를 알고 있다.

    // sizeof 소개
    cout << i << " " << sizeof(i) << endl; //
    // 123 4 - 4byte라는 의미.

    cout << sizeof(int) << endl;
    // 4 - int 자체가 4byte를 가지고 있는듯?

    float f = 123.456f; // 마지막 f 주의 - 많이 사용
    double d = 123.456; // f 불필요

    cout << f << "  " << sizeof(f) << endl; // 123.456 4
    cout << d << "  " << sizeof(f) << endl; //

    // C++는 글자 하나와 문자열을 구분합니다.
    char c = 'a';
    char str[] = "Hello, World!"; // 대괄호는 배열을 만든다는 의미이다.

    cout << c << "  " << sizeof(c) << endl; // a 1

    // 그 외에도 다양한 자료형이 존재합니다.

    // 형변환
    i = 986.654; // double을 int에 강제로 저장?

    cout << "int from double" << i << endl; // 정답은 987이 나옴 - 버림을 한다.

    f = 567.89; // 이것도 형변환 - f가 붙어져 있지 않아서 double임

    // 기본 연산자

    // i = 987;
    i += 100;
    i ++; // 1을 증가시켜라

    cout << i << endl; // 1088?

    // 불리언
    bool is_good = true;
    is_good = false;

    cout << is_good << endl; // 0 false는 0이고 true는 1이다.

    cout << boolalpha << true << endl; // true
    cout << is_good << endl; // false
    cout << noboolalpha << endl;

    cout << (true && true) << endl; // 추측해보세요 - 괄호로 연산 먼저하게 만들어야 한다.

    // 영역(scope)

    i = 123;

    {
        int i = 345;
        cout << i << endl; // 안쪽 영역을 먼저보기 때문에 123 만약 i를 정의를 안 하면 123 자기 영역 보고 더 넓은 영역 순서
    }

    // int i = 345; 만약 괄호를 지우면 에러 남 - 한 영역에서 같은 이름을 선언할 수 없음

    cout << i << endl; // 영역이 다르기 때문에 123

    return 0;

}
