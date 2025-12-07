import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { v4 as uuidv4 } from 'uuid';

const MetadataFormComponent = ({ capturedImage, onSearch, isLoading }) => {
    const { register, handleSubmit, formState: { errors } } = useForm();
    const [privacyAgreed, setPrivacyAgreed] = useState(false);

    const onSubmit = async (data) => {
        if (!privacyAgreed) {
            alert('Please agree to the privacy policy');
            return;
        }

        const payload = {
            session_id: uuidv4(),
            user_name: data.userName,
            captured_image: capturedImage,
            privacy_policy_agreed: privacyAgreed,
            timestamp: new Date().toISOString(),
        };

        onSearch(payload);
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-md">
            {/* Name Input */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Name
                </label>
                <input
                    type="text"
                    placeholder="Enter your full name"
                    {...register('userName', {
                        required: 'Name is required',
                        minLength: { value: 2, message: 'Name must be at least 2 characters' },
                    })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                {errors.userName && (
                    <p className="text-red-500 text-sm mt-1">{errors.userName.message}</p>
                )}
            </div>

            {/* Privacy Policy */}
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <label className="flex items-start gap-3 cursor-pointer">
                    <input
                        type="checkbox"
                        checked={privacyAgreed}
                        onChange={(e) => setPrivacyAgreed(e.target.checked)}
                        className="mt-1 w-4 h-4 text-teal-500 rounded focus:ring-2 focus:ring-teal-500"
                    />
                    <span className="text-sm text-gray-700">
                        I agree to the{' '}
                        <a href="/privacy" className="text-teal-600 hover:underline">
                            Privacy Policy
                        </a>
                        . I understand that my facial image will be temporarily stored for analysis and automatically deleted after 24 hours.
                    </span>
                </label>
            </div>

            {/* Search Button */}
            <button
                type="submit"
                disabled={isLoading || !privacyAgreed}
                className={`w-full px-4 py-3 rounded-lg font-semibold text-white transition ${isLoading || !privacyAgreed
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-teal-500 hover:bg-teal-600 cursor-pointer'
                    }`}
            >
                {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                        <div className="animate-spin h-4 w-4 border-b-2 border-white"></div>
                        Searching...
                    </span>
                ) : (
                    '🔍 Search Photos'
                )}
            </button>
        </form>
    );
};

export default MetadataFormComponent;
